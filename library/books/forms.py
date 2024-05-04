from django import forms
from django.core.exceptions import ValidationError

from .models import Book


class BookForm(forms.ModelForm):
	name = forms.CharField(max_length=255)
	author = forms.CharField(max_length=255)
	preview = forms.Textarea()
	date_written = forms.DateField()

	class Meta:
		model = Book
		fields = [
			'name',
			'author',
			'preview',
			'date_written',
		]

	def clean(self):
		cleaned_data = super().clean()
		preview = cleaned_data.get('preview')
		name = cleaned_data.get('name')

		if preview == name:
			raise ValidationError('Название не должно быть идентично превью')

		return cleaned_data
