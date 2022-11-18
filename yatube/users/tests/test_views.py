from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.forms import forms

User = get_user_model()


class UserViewTest(TestCase):
    @classmethod
    def setUp(self):
        self.guest_client = Client()

    def test_correct_HTML_templates(self):
        templates = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:login'): 'users/login.html',
        }
        for url, template in templates.items():
            response = self.guest_client.get(url)
            with self.subTest(url=url):
                self.assertTemplateUsed(response, template,
                                        'Не совпадает шаблон')

    def test_correct_context_create_user(self):
        """Проверка значений в форме users:signup"""
        response = self.guest_client.get(reverse('users:signup'))
        form_fields = {
            'password1': forms.PasswordInput,
            'password2': forms.PasswordInput
        }
        form = response.context['form']
        for value, field in form_fields.items():
            with self.subTest(value=value):
                self.assertIsInstance(form.fields[value].widget, field)
        self.assertIsInstance(form.fields['username'], forms.CharField)
