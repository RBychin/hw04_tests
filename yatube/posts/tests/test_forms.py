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
        cls.post = Post.objects.create(
            text='Ля ля ля',
            group=cls.group,
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorize_client = Client()
        self.authorize_client.force_login(self.user)

    def test_post_form(self):
        """Проверка добавление поста с валидной формой."""
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
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Созданный пост',
                group=self.group,
            ).exists()
        )

    def test_post_edit_form(self):
        """Проверка работы изменения поста с валидной формой."""
        response = self.authorize_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.pk
            }),
            data={'text': 'Измененный пост',
                  'group': self.group.pk}
        )
        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': self.post.pk})
        )
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Измененный пост',
                group=self.group,
            ).exists()
        )

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
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data={'title': ' '}
        )
        self.assertFormError(response, 'form', 'text', 'Обязательное поле.')
        self.assertEqual(response.status_code, HTTPStatus.OK, 'Сервер упал')
