from django.views.generic import (
	ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.core.cache import cache

from .models import Book, Cart
from .forms import BookForm
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
			if action == 'addcart':
				cart_exists = Cart.objects.filter(user=request.user).exists()
				if cart_exists:
					cart = Cart.objects.get(user=request.user)
				else:
					cart = Cart.objects.create(user=request.user)

				book = Book.objects.get(pk=request.POST['book_id'])
				cart.books.add(book)
				cart.save()
		return redirect('/')


class CartView(PermissionRequiredMixin, ListView):
	permission_required = ('books.view_book',)
	template_name = 'books_app/cart.html'
	context_object_name = 'books'

	def get_queryset(self):
		cart = Cart.objects.get(user=self.request.user)
		return cart.books.all()

	def get_context_data(self, *args, **kwargs):
		context_data = super().get_context_data(*args, **kwargs)
		if self.request.user.is_authenticated:
			context_data['one_time_code'] = Cart.objects.get(user=self.request.user).one_time_code

		return context_data

	def post(self,request):
		if 'action' in request.POST:
			action = request.POST['action']
			if action == 'buy':
				one_time_code = ''
				random.seed(time.time())
				for _ in range(16):
					one_time_code += random.choice(string.ascii_letters)
				split_ids = request.POST['books'].rstrip(',').split(',')
				books_list = list(map(int, split_ids))
				books = list(Book.objects.filter(id__in=books_list).values_list('name', flat=True))

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


class BookAdd(CreateView):
	form_class = BookForm
	model = Book
	template_name = 'books_app/book_edit.html'
	success_url = '/'