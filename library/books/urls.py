from django.urls import path

from .views import BookDetail, Library, BookAdd, CartView

urlpatterns = [
	path('', Library.as_view(), name='library'),
	path('<int:pk>', BookDetail.as_view(), name='book_detail'),
	path('book/add/', BookAdd.as_view(), name='book_add'),
	path('cart/', CartView.as_view(), name='cart'),
]