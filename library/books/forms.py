from django import forms
from django.core.exceptions import ValidationError
from django.core.cache import cache

from .models import Book


class BookForm(forms.ModelForm):
	name = forms.CharField(max_length=255, label='Название')
	author = forms.CharField(max_length=255, label='Автор')
	preview = forms.CharField(widget=forms.Textarea(), label='Превью')
	date_written = forms.DateField(label='Дата написания')

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


class OneTimeCodeForm(forms.Form):
	code = forms.CharField(max_length=125, label='Код')

	def clean(self):
		cleaned_data = super().clean()
		code = cleaned_data.get('code')
		code = code.strip(' ')
		books = cache.get(code)

		if books:

			cache.delete(f'{code}')
			return cleaned_data
		else:
			raise ValidationError('Код введён неправильно')