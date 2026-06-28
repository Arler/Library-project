from django.contrib import admin

from .models import Book, BookLoan, Cart
# Register your models here.

class BookLoanAdmin(admin.ModelAdmin):
	list_display = ('loan_date', 'return_date')


class CartAdmin(admin.ModelAdmin):
	filter_horizontal = ['books']


admin.site.register(Book)
admin.site.register(BookLoan, BookLoanAdmin)
admin.site.register(Cart, CartAdmin)