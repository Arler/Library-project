from django.urls import path

from .views import BookDetail, Library, CartView, issuance_view, order

urlpatterns = [
	path('', Library.as_view(), name='library'),
	path('<int:pk>', BookDetail.as_view(), name='book_detail'),
	path('cart/', CartView.as_view(), name='cart'),
	path('issuance/', issuance_view, name='issuance'),
	path('order/', order, name='order')
]