from django.urls import reverse
from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..forms import CreationForm


User = get_user_model()


class UserTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CreationForm

    def setUp(self):
        self.guest_client = Client()

    def test_new_user_create_valid_form(self):
        """Создание нового пользователя с валидной формой
        и работа редиректа."""
        users_count = User.objects.count()
        form_data = {
            'username': 'new_user',
            'password1': '5Rk1f2zQ',
            'password2': '5Rk1f2zQ'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data
        )
        self.assertEqual(User.objects.count(), users_count + 1,
                         'Не удается создать нового пользователя')
        self.assertEqual(
            User.objects.get(username='new_user'
                             ).username, 'new_user')
        self.assertRedirects(
            response, reverse('posts:index')
        )

    def test_new_user_create_not_valid_form(self):
        """Создание нового пользователя с НЕ валидной формой
                и работа редиректа."""
        #  Вроде этот валидатор проверять не нужно (он встроенный,
        #  но в доп задании была такая задача).
        users_count = User.objects.count()
        form_data = {
            'username': 'new_user',
            'password1': 'qwerty12',
            'password2': 'qwerty12'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data
        )
        self.assertEqual(User.objects.count(), users_count,
                         'Проверьте работу валидаторов.')
        self.assertFormError(
            response, 'form', 'password2',
            'Введённый пароль слишком широко распространён.'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, 'Сервер упал.')
