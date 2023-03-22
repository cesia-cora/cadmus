from django.test import TestCase
from django.template.defaultfilters import slugify
from django.urls import reverse, resolve
from cadmus.models import *
from cadmus.views import *

class TestModels(TestCase):
    def test_entry_creation(self):
        user = User.objects.create(username='user', email='example123@example3.com')
        user.set_password('abc123')
        user.save()

        entry = Entry.objects.create(title='Testing', slug='testingxy', content='Lorem ipsum', creator=user)
        entry.save()

        self.assertEqual(str(user), 'user')
        self.assertEqual(user.email, 'example123@example3.com')
        self.assertEqual(str(entry.title), 'Testing')
        self.assertEqual(str(entry.slug), 'testingxy')
        self.assertEqual(str(entry.content), 'Lorem ipsum')
        self.assertEqual(entry.creator, user)