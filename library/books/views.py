from django.views.generic import (
	ListView, DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.core.cache import cache

from .models import Book, Cart, BookLoan
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
		context_data['cart'] = Cart.objects.get(user=self.request.user)
		return context_data



class CartView(LoginRequiredMixin, ListView):
	model = Cart
	login_url = "/accounts/login/"
	template_name = 'books_app/cart.html'
	context_object_name = 'cart'

	def get_queryset(self):
		return Cart.objects.get(user=self.request.user) 

	# def get_context_data(self, *args, **kwargs):
	# 	context_data = super().get_context_data(*args, **kwargs)
	# 	if self.request.user.is_authenticated:
	# 		context_data['one_time_code'] = Cart.objects.get(user=self.request.user).one_time_code

	# 	return context_data

	def post(self,request):
		if 'action' in request.POST:
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
			if action == 'remove':
				book = Book.objects.get(pk=request.POST['book'])
				cart = Cart.objects.get(user=request.user)
				cart.books.remove(book)
				cart.save()

		return redirect('/cart/')


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
	issuet_books = BookLoan.objects.filter(user=request.user)
	context = {'books': issuet_books}
	return render(request, 'books_app/order.html', context=context)