from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from ckeditor.fields import RichTextField
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken

# Local helper
def _get_fernet():
	key = getattr(settings, "ENCRYPTION_KEY", None)
	if not key:
		raise ValueError("ENCRYPTION_KEY is not set in settings")
	if isinstance(key, str):
		key = key.encode()
	return Fernet(key)

class User(AbstractUser):
	pass

class Entry(models.Model):
	title = models.CharField(blank=False, max_length=200, verbose_name="Title")
	slug = models.SlugField(max_length=200, blank=False, null=True, verbose_name="Slug")
	content = CKEditor5Field(null=True)
	initial_time = models.DateTimeField(default=timezone.now, blank=True, null=False, verbose_name="Initial Time")
	last_modified = models.DateTimeField(auto_now=True, null=True, verbose_name="Last Modified")
	creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

	def __str__(self):
		return f"{self.title}"

	# Model methods
	def save(self, *args, **kwargs):
		if self.content and not str(self.content).startswith("gAAAA"):
			try:
				f = _get_fernet()
				encrypted = f.encrypt(str(self.content).encode("utf-8"))
				self.content = encrypted.decode("utf-8")
			except Exception:
				pass
		super().save(*args, **kwargs)

	@property
	def decrypted_content(self):
		if not self.content:
			return ""
		try:
			if not str(self.content).startswith("gAAAA"):
				return str(self.content)
			f = _get_fernet()
			plain = f.decrypt(str(self.content).encode("utf-8"))
			return plain.decode("utf-8")
		except (InvalidToken, Exception):
			return ""