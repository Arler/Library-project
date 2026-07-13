from django.views.generic import (
	ListView, DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.core.cache import cache

from .models import Book, Cart, BookLoan, BookReturn
import random, time, string

class BookDetail(DetailView):
	model = Book
	template_name = 'books_app/book.html'
	context_object_name = 'book'


class Library(ListView):
	model = Book
	ordering = '-date_written'
	template_name = 'books_app/library.html'
	context_object_name = 'books'
	paginate_by = 10

	def post(self,request):
		if 'action' in request.POST:
			action = request.POST['action']
			cart = Cart.objects.get(user=request.user)
			if not cart:
				cart = Cart.objects.get(user=request.user)
			if action == 'addcart':
				book = Book.objects.get(pk=request.POST['book_id'])
				cart.books.add(book)
				cart.save()
			if action == 'removecart':
				book = Book.objects.get(pk=request.POST['book_id'])
				cart.books.remove(book)
				cart.save()
		return redirect('/')
	
	def get_queryset(self):
		return Book.objects.filter(issuet=False)
	
	def get_context_data(self, **kwargs):
		context_data = super().get_context_data(**kwargs)
		if self.request.user.is_authenticated:
			context_data['cart'] = Cart.objects.get(user=self.request.user)
		return context_data


@login_required
def cart_view(request):

	if request.method == 'POST':
		action = request.POST['action']
		if action == 'buy' and request.POST['books']:
			one_time_code = ''
			random.seed(time.time())
			for _ in range(16):
				one_time_code += random.choice(string.ascii_letters)
			split_ids = request.POST['books'].rstrip(',').split(',')
			books_list = list(map(int, split_ids))
			books = Book.objects.filter(id__in=books_list).all()

			cache.set(f'{one_time_code}', books)
			cart = Cart.objects.get(user=request.user)
			cart.one_time_code = one_time_code
			cart.save()
		elif action == 'remove':
			book = Book.objects.get(pk=request.POST['book'])
			cart = Cart.objects.get(user=request.user)
			cart.books.remove(book)
			cart.save()

		return redirect('/cart/')
	
	context = {'cart': Cart.objects.get(user=request.user)}
	return render(request, 'books_app/cart.html', context=context)


@login_required
def issuance_view(request):
	cart = Cart.objects.get(user=request.user)
	context = {'one_time_code': cart.one_time_code}

	if request.method == 'POST' and request.POST.get('action') == 'issuance':
		code = request.POST.get('code')
		books = cache.get(code)
		if books:
			book_loan = BookLoan.objects.create(user=request.user)
			context['books'] = books

			for book in books:
				book.issuet = True
				book_loan.books.add(book)
				book.save()

			book_loan.save()
			cart.books.clear()
			cache.delete(code)

	return render(request, 'books_app/issuance.html', context)

@login_required
def order(request):
	active_loans = BookLoan.objects.filter(user=request.user).exclude(id__in=BookReturn.objects.values_list('loan', flat=True))
	issuet_books = Book.objects.filter(bookloan__in=active_loans)
	context = {'books': issuet_books}
	return render(request, 'books_app/order.html', context=context)

@login_required
def return_view(request):

	if not cache.has_key(f'return_books_{request.user}'):
		cache.set(f'return_books_{request.user}', set())
	return_books = cache.get(f'return_books_{request.user}')
	if 'action' in request.POST:
		action = request.POST['action']
		if action == 'addreturn':								# Добавление возвращаемой книги в соответствующий список для дальнейшего возврата
			return_books.add(int(request.POST['book_id']))
			cache.set(f'return_books_{request.user}', return_books)
			return_books = list(cache.get(f'return_books_{request.user}'))
		elif action == 'removereturn':							# Удаление возвращаемой книги из списка
			return_books.discard(int(request.POST['book_id']))
			cache.set(f'return_books_{request.user}', return_books)
			return_books = list(cache.get(f'return_books_{request.user}'))
		elif action == 'return':									# Возврат выбранных книг
			book_loans = BookLoan.objects.filter(books__id__in=return_books, user=request.user).exclude(id__in=BookReturn.objects.values_list('loan', flat=True))
			for book_loan in book_loans:
				book_return = BookReturn.objects.create(user=request.user, loan=book_loan)
				related_books_ids = set(book_loan.books.all().values_list('id', flat=True)) & return_books
				for book in Book.objects.filter(id__in=related_books_ids):
					book.issuet = False
					book.save()
					book_return.books.add(book)
				not_returned_books = book_loan.books.all().filter(issuet=True)
				if not_returned_books:
					new_book_loan = BookLoan.objects.create(
						user=request.user,
						loan_date=book_loan.loan_date,
						return_date=book_loan.return_date
						)
					new_book_loan.books.set(not_returned_books)
					new_book_loan.save()
				book_return.save()
			cache.delete(f'return_books_{request.user}')

	active_loans = BookLoan.objects.filter(user=request.user).exclude(id__in=BookReturn.objects.values_list('loan', flat=True))
	issuet_books = Book.objects.filter(bookloan__in=active_loans)
	context = {
		'issuet_books': issuet_books,
		'return_books': list(return_books)
		}
	return render(request, 'books_app/return.html', context=context)
