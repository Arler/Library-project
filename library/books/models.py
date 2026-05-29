from django.db import models

from accounts.models import User


class Book(models.Model):
    name = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    preview = models.TextField()
    date_written = models.DateField()
    rack = models.CharField(max_length=30, blank=True)
    shelf = models.CharField(max_length=30, blank=True)
    issuet = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book)
    one_time_code = models.CharField(max_length=32, blank=True)


class BookLoan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book)
    loan_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Выдача книги'
        verbose_name_plural = 'Учёт выдачи книг'

    def __str__(self):
        return f'{self.user}'
