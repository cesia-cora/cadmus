from django.test import SimpleTestCase
from django.urls import reverse, resolve
from cadmus.models import *
from cadmus.views import *

class TestUrls(SimpleTestCase):

    def test_index_url_is_resolved(self):
        url = reverse('cadmus:index')
        self.assertEquals(resolve(url).func, index)

    def test_register_url_is_resolved(self):
        url = reverse('cadmus:register')
        self.assertEquals(resolve(url).func, register)

    def test_login_url_is_resolved(self):
        url = reverse('cadmus:login')
        self.assertEquals(resolve(url).func, login_view)

    def test_logout_url_is_resolved(self):
        url = reverse('cadmus:logout')
        self.assertEquals(resolve(url).func, logout_view)

    def test_list_url_is_resolved(self):
        url = reverse('cadmus:create')
        self.assertEquals(resolve(url).func, create_entry)

    def test_entry_url_is_resolved(self):
        url = reverse('cadmus:entry', args=['slug'])
        self.assertEquals(resolve(url).func, entry)

    def test_edit_url_is_resolved(self):
        url = reverse('cadmus:edit', args=['slug'])
        self.assertEquals(resolve(url).func, edit_entry)

    def test_delete_url_is_resolved(self):
        url = reverse('cadmus:delete', args=['slug'])
        self.assertEquals(resolve(url).func, delete_entry)