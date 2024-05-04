from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from django import forms


class CustomSignupForm(SignupForm):
	last_name = forms.CharField(max_length=150, label="Фамилия")
	first_name = forms.CharField(max_length=150, label="Имя")
	surname = forms.CharField(max_length=150, label="Отчество")

	def save(self, request):
		user = super(CustomSignupForm, self).save(request)
		user.last_name = self.cleaned_data.get('last_name')
		user.first_name = self.cleaned_data.get('first_name')
		user.surname = self.cleaned_data['surname']
		user.username = f'{user.last_name} {user.first_name} {user.surname}'
		users = Group.objects.get(name="Пользователи")
		user.groups.add(users)
		user.save()
		return user
