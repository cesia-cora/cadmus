from django import forms
from concurrency.forms import ConcurrentForm
from .models import *
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django_ckeditor_5.widgets import CKEditor5Widget

class EntryForm(ConcurrentForm):
	tags = forms.ModelMultipleChoiceField(
		queryset=Tag.objects.none(),
		required=False,
		widget=forms.SelectMultiple(attrs={'class': 'select is-multiple'})
	)
	new_tags = forms.CharField(required=False, help_text='Comma-separated new tags', widget=forms.TextInput(attrs={'placeholder': 'tag1, tag2'}))

	class Meta:
		model = Entry
		fields = ['title', 'slug', 'content', 'initial_time', 'tags', 'version']
		widgets = {'title': forms.TextInput(attrs={'placeholder': 'Type your title here', 'class': 'input self-input-post', 'type': 'text'}),
		'slug': forms.TextInput(attrs={'placeholder': 'Type something like "this-is-my-entry"', 'class': 'input self-input-post',}),
		'content': CKEditor5Widget(attrs={'placeholder': 'Type your entry here', 'class': 'django_ckeditor_5'}, config_name='extends'),
		'initial_time': forms.DateTimeInput(attrs={'class': 'input self-input-post', 'type': 'datetime-local'}),
		'version': forms.HiddenInput()
		}

	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user', None)
		super().__init__(*args, **kwargs)
		if user:
			self.fields['tags'].queryset = Tag.objects.filter(creator=user)
	
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

class PasswordRecoveryForm(forms.Form):
	identifier = forms.CharField(
		label="Email or username",
		widget=forms.TextInput(attrs={'placeholder': 'Email or username', 'class': 'input is-normal'})
	)
	recovery_code = forms.CharField(
		label="Master Key",
		widget=forms.TextInput(attrs={'placeholder': 'Your 12-character code', 'class': 'input is-normal'})
	)
	new_password1 = forms.CharField(
		label="New Password",
		widget=forms.PasswordInput(attrs={'placeholder': 'New password', 'class': 'input is-normal'})
	)
	new_password2 = forms.CharField(
		label="Confirm New Password",
		widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password', 'class': 'input is-normal'})
	)

	def clean(self):
		cleaned_data = super().clean()
		p1 = cleaned_data.get("new_password1")
		p2 = cleaned_data.get("new_password2")

		if p1 != p2:
			raise forms.ValidationError("The new passwords do not match.")
		if p1:
			validate_password(p1)
		return cleaned_data