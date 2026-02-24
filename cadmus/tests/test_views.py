from unittest import patch, Mock
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from cadmus.models import *
from cadmus import views

User = get_user_model()

def make_request(method='post', path='/', data=None, user=None):
    rf = RequestFactory()
    req = getattr(rf, method)(path, data=data or {})
    req.user = user or AnonymousUser()

    SessionMiddleware(lambda r: HttpResponse()).process_request(req)
    req.session.save()
    MessageMiddleware(lambda r: HttpResponse()).process_request(req)
    return req

class TestViews(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.index_view = reverse('cadmus:index')
        self.login_view = reverse('cadmus:login')
        self.logout_view = reverse('cadmus:logout')
        self.register_view = reverse('cadmus:register')
        self.create_view = reverse('cadmus:create')
        self.entry_view = reverse('cadmus:entry', args=['testingxyz'])
        self.edit_view = reverse('cadmus:edit', args=['testingxyz'])
        self.delete_view = reverse('cadmus:delete', args=['testingxyz'])
    
        user = User.objects.create(username='user', email='example123@example3.com')
        user.set_password('abc123')
        user.save()
        self.client.login(username='user', password='abc123')

        Entry.objects.create(title='This is a test',
            slug='testingxyz',
            content='This is text for the test',
            creator=user)

    def test_index_view(self):
        response = self.client.get(self.index_view)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cadmus/index.html')

    def test_login_view(self):
        response = self.client.get(self.login_view)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cadmus/login.html')

    def test_logout_view(self):
        response = self.client.get(self.logout_view)
        self.assertEqual(response.status_code, 302)

    def test_register_view(self):
        response = self.client.get(self.register_view)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cadmus/register.html')

    def test_create_view(self):
        response = self.client.get(self.create_view)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cadmus/create_entry.html')

    def test_entry_view(self):
        response = self.client.get(self.entry_view)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cadmus/entry.html')

    def test_edit_view(self):
        fr_response = self.client.get(self.edit_view)
        response = self.client.post(self.edit_view, {
            'title': 'New title test',
            'slug': 'testingxyz',
            'content': 'New added text for the test'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(fr_response.status_code, 200)
        self.assertTemplateUsed(fr_response, 'cadmus/update_entry.html')

    def test_delete_view(self):
        response = self.client.get(self.delete_view)
        self.assertEqual(response.status_code, 302)

class TransactionAndLockingTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="tester", email="t@e.com", password="pass123")
        self.entry = Entry.objects.create(title="T", slug="t-slug", content="c", creator=self.user)

    def test_edit_entry_uses_select_for_update(self):
        req = make_request('post', f'/entries/{self.entry.slug}/edit', data={'title': 'New', 'content': 'new'}, user=self.user)
        with patch('cadmus.views.Entry.objects.select_for_update') as mock_select:
            mock_qs = Mock()
            mock_qs.get.return_value = self.entry
            mock_select.return_value = mock_qs
            resp = views.edit_entry(req, self.entry.slug)
            assert mock_select.called

    def test_delete_entry_uses_select_for_update(self):
        req = make_request('post', f'/entries/{self.entry.slug}/delete', user=self.user)
        with patch('cadmus.views.Entry.objects.select_for_update') as mock_select:
            mock_qs = Mock()
            mock_qs.get.return_value = self.entry
            mock_select.return_value = mock_qs
            resp = views.delete_entry(req, self.entry.slug)
            assert mock_select.called