from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from ckeditor.fields import RichTextField

class User(AbstractUser):
	pass

class Entry(models.Model):
	title = models.CharField(blank=False, max_length=200, verbose_name="")
	slug = models.SlugField(max_length=200, blank=False, null=True, verbose_name="")
	content = RichTextField(null=True)
	initial_time = models.DateTimeField(default=timezone.now, blank=True, null=False, verbose_name="")
	last_modified = models.DateTimeField(auto_now=True, null=True)
	creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

	def __str__(self):
		return f"{self.title}"