from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.crypto import get_random_string
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken
from concurrency.fields import AutoIncVersionField

# Local helper
def _get_fernet():
	key = getattr(settings, "ENCRYPTION_KEY", None)
	if not key:
		raise ValueError("ENCRYPTION_KEY is not set in settings")
	if isinstance(key, str):
		key = key.encode()
	return Fernet(key)

class User(AbstractUser):
	recovery_code_encrypted = models.BinaryField(null=True, blank=True)

	def generate_recovery_code(self):
		raw_code = get_random_string(length=12, allowed_chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789')
		f = _get_fernet()
        
		self.recovery_code_encrypted = f.encrypt(raw_code.encode("utf-8"))
		self.save()
        
		return raw_code

	def check_recovery_code(self, raw_code):
		if not self.recovery_code_encrypted:
			return False
		f = _get_fernet()
		
		try:
			decrypted_code = f.decrypt(self.recovery_code_encrypted).decode("utf-8")
			return decrypted_code == raw_code
		except (InvalidToken, Exception):
			return False

class Entry(models.Model):
	title = models.CharField(blank=False, max_length=200, verbose_name="Title")
	slug = models.SlugField(max_length=200, blank=False, null=True, verbose_name="Slug")
	content = CKEditor5Field(null=True)
	initial_time = models.DateTimeField(default=timezone.now, blank=True, null=False, verbose_name="Initial Time")
	last_modified = models.DateTimeField(auto_now=True, null=True, verbose_name="Last Modified")
	creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	tags = models.ManyToManyField('Tag', related_name='tags', blank=True)
	version = AutoIncVersionField(default=1, verbose_name="Version")

	class Meta:
		indexes = [
			models.Index(fields=['initial_time']),
			models.Index(fields=['slug']),
			models.Index(fields=['creator']),
		]

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

class Tag(models.Model):
	name = models.CharField(max_length=50, unique=True, verbose_name="Tag Name")
	creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

	class Meta:
		unique_together = ('creator', 'name')
		indexes = [
			models.Index(fields=['name']),
		]

	def __str__(self):
		return self.name