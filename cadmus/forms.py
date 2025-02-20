from django import forms
from django.forms import ModelForm
from .models import *

class EntryForm(ModelForm):
	class Meta:
		model = Entry
		fields = ['title', 'slug', 'content', 'initial_time']
		widgets = {'title': forms.TextInput(attrs={'placeholder': 'Type your title here', 'class': 'input self-input-post', 'type': 'text'}),
		'slug': forms.TextInput(attrs={'placeholder': 'Type something like "this-is-my-entry"', 'class': 'input self-input-post',}),
		'content': forms.Textarea(attrs={'placeholder': 'Type your entry here', 'class': 'textarea self-input-post'}),
		'initial_time': forms.DateTimeInput(attrs={'class': 'input self-input-post'})}
	
	def clean_slug(self):
		slug = self.cleaned_data.get('slug')
		if Entry.objects.exclude(id=self.instance.id).filter(slug=slug).exists():
			raise forms.ValidationError('This slug already exists. Please, type another one.')
		return slug
