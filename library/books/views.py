from django.views.generic import (
	ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.shortcuts import redirect

from .models import Book, Cart
from .forms import BookForm


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


class CartView(ListView):
	template_name = 'books_app/cart.html'
	context_object_name = 'books'

	def get_queryset(self):
		cart = Cart.objects.get(user=self.request.user)
		return cart.books.all()


class BookAdd(CreateView):
	form_class = BookForm
	model = Book
	template_name = 'books_app/book_edit.html'
	success_url = '/'