from django.contrib import admin

from .models import Book, BookLoan
# Register your models here.

class BookLoanAdmin(admin.ModelAdmin):
	list_display = ('loan_date', 'return_date')


admin.site.register(Book)
admin.site.register(BookLoan, BookLoanAdmin)