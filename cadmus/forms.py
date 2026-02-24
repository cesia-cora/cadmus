from django import forms
from django.forms import ModelForm
from .models import *
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy
from django_ckeditor_5.widgets import CKEditor5Widget

class EntryForm(ModelForm):
	class Meta:
		model = Entry
		fields = ['title', 'slug', 'content', 'initial_time']
		widgets = {'title': forms.TextInput(attrs={'placeholder': 'Type your title here', 'class': 'input self-input-post', 'type': 'text'}),
		'slug': forms.TextInput(attrs={'placeholder': 'Type something like "this-is-my-entry"', 'class': 'input self-input-post',}),
		'content': CKEditor5Widget(attrs={'placeholder': 'Type your entry here', 'class': 'django_ckeditor_5'}, config_name='extends'),
		'initial_time': forms.DateTimeInput(attrs={'class': 'input self-input-post'})}
	
	def clean_slug(self):
		slug = self.cleaned_data.get('slug')
		if Entry.objects.exclude(id=self.instance.id).filter(slug=slug).exists():
			raise forms.ValidationError('This slug already exists. Please, type another one.')
		return slug

class UsernameChangeForm(forms.Form):
	def __init__(self, user, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.user = user

	username = forms.CharField(
		label="New username",
		max_length=150,
		error_messages={'required': ''},
		widget=forms.TextInput(
			attrs={
				'placeholder': 'New username',
				'class': 'input is-normal',
			}
		),
	)

def clean_username(self):
	User = get_user_model()
	username = self.cleaned_data.get("username")

	if username == self.user.username:
		raise forms.ValidationError("You are already using this username.")

	if User.objects.exclude(pk=self.user.pk).filter(username=username).exists():
		raise forms.ValidationError("This username is already taken.")
		
	return username

class PasswordChangeForm(forms.Form):
	def __init__(self, user, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.user = user
		self.fields['current_password'].widget = forms.PasswordInput(
			attrs={'placeholder': 'Current password', 
			'class': 'input is-normal'})
		self.fields['new_password1'].widget = forms.PasswordInput(
			attrs={'placeholder': 'New password',
			'class': 'input is-normal'})
		self.fields['new_password2'].widget = forms.PasswordInput(
			attrs={'placeholder': 'Confirm new password',
			'class': 'input is-normal'})

	current_password = forms.CharField(
		label=('Current password'), 
		error_messages={'required': ''},
		widget=forms.PasswordInput,
		)
	new_password1 = forms.CharField(
		label=("New password"), 
		error_messages={'required': ''},
		widget=forms.PasswordInput,
		)
	new_password2 = forms.CharField(
		label=("Confirm new password"), 
		error_messages={'required': ''},
		widget=forms.PasswordInput,
		)

	def clean_current_password(self):
		cp = self.cleaned_data.get("current_password")
		if not self.user.check_password(cp):
			raise forms.ValidationError(_("Current password is incorrect."))
		return cp

	def clean_password(self):
		cleaned = super().clean()
		p1 = cleaned.get("new_password1")
		p2 = cleaned.get("new_password2")
		if p1 and p2 and p1 != p2:
			raise forms.ValidationError(_("The two new password fields didn't match."))
		if p1:
			validate_password(p1, self.user)
		return cleaned