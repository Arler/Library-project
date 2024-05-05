from django.db import models

from accounts.models import User

class Book(models.Model):
    name = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    preview = models.TextField()
    date_written = models.DateField()


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book)
    one_time_code = models.CharField(max_length=32, blank=True)
