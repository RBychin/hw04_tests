from django.contrib.auth import get_user_model
from django.urls import reverse
from http import HTTPStatus

from ..forms import PostForm
from ..models import Post, Group
from django.test import TestCase, Client

User = get_user_model()


class FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm
        cls.user = User.objects.create_user(
            username='roman'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        Post.objects.create(
            text='Ля ля ля',
            group=cls.group,
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorize_client = Client()
        self.authorize_client.force_login(self.user)

    def test_post_form(self):
        """Проверка добавление поста через с валидной формой."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Созданный пост',
            'group': self.group.pk
        }
        response = self.authorize_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertRedirects(
            response, reverse('posts:profile',
                              kwargs={'username': self.user.username})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(Post.objects.first().text, 'Созданный пост')

    def test_post_edit_form(self):
        """Проверка работы изменения поста с валидной формой."""
        response = self.authorize_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': '1'
            }),
            data={'text': 'Измененный пост'}
        )
        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': '1'})
        )
        self.assertEqual(Post.objects.first().text, 'Измененный пост')

    def test_post_create_not_valid_form(self):
        """Проверка работы добавления поста с невалидной формой."""
        post_count = Post.objects.count()
        response = self.authorize_client.post(
            reverse('posts:post_create'),
            data={'text': ' '}
        )
        self.assertFormError(response, 'form', 'text', 'Обязательное поле.')
        self.assertEqual(Post.objects.count(),
                         post_count, 'Пост не должен быть добавлен')
        self.assertEqual(response.status_code, HTTPStatus.OK, 'Сервер упал')

    def test_post_edit_not_valid_form(self):
        """Проверка работы изменения поста с невалидной формой."""
        response = self.authorize_client.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data={'title': ' '}
        )
        self.assertFormError(response, 'form', 'text', 'Обязательное поле.')
        self.assertEqual(response.status_code, HTTPStatus.OK, 'Сервер упал')

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
