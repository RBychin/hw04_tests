from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group
from django import forms

User = get_user_model()


class PostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создается 14 постов одной группы и одного автора,
        так же создается 3 поста от другого автора, в другой группе,
        который не должен учитываться в выводе количества постов контекста,
        для убедительности верности проверки, благодаря этому,
        так же проверяется, что пост не попадает в другую группу или
        другому автору."""

        super().setUpClass()
        #  группа не участвует в подсчете вывода (кроме index)
        uncount_group = Group.objects.create(
            title='Тестовая группа2',
            slug='test_slug_2'
        )
        #  автор не участвует в подсчете вывода (кроме index)
        uncount_author = User.objects.create_user(username='test_user')
        #  пост не участвует в подсчете вывода (кроме index)
        for i in range(3):
            Post.objects.create(
                text=f'Тестовый текст {i}',
                group=uncount_group,
                author=uncount_author
            )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug'
        )
        cls.user = User.objects.create_user(
            username='roman'
        )
        for i in range(14):
            cls.post = Post.objects.create(
                text=f'Тестовый текст {i}',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorize_client = Client()
        self.authorize_client.force_login(self.user)

    def test_correct_HTML_templates(self):
        """Проверка корректности шаблонов и адресов."""
        templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'test_slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'roman'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': '1'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': '4'}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for url, template in templates.items():
            with self.subTest(url=url):
                response = self.authorize_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_paginator_first_page(self):
        """Тестирование первой страницы паджинатора для Главной страницы,
        Страницы группы, Страницы профиля."""
        addresses = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'roman'})
        )
        for address in addresses:
            response = self.authorize_client.get(address)
            with self.subTest(address=address):
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_paginator_second_page(self):
        """Тестирование второй страницы паджинатора для Главной страницы,
        Страницы группы, Страницы профиля."""
        addresses = (
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'roman'})
        )
        for address in addresses:
            response = self.authorize_client.get(address + '?page=2')
            with self.subTest(address=address):
                self.assertEqual(len(response.context['page_obj']), 4)

    def test_context(self):
        """Тест контекста главной страницы."""
        response = self.authorize_client.get(reverse('posts:index'))
        first_obj = response.context['page_obj'][0]
        context = {
            first_obj.group.title: 'Тестовая группа',
            first_obj.text: 'Тестовый текст 13',
            first_obj.author.username: 'roman',
            first_obj.group.slug: 'test_slug'
        }
        for field, value in context.items():
            with self.subTest(context=field):
                self.assertEqual(field, value)

    def test_context_post_detail(self):
        """Тест контекста для post_detail"""
        response = self.authorize_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': '3'}
        ))
        post = response.context['post']
        self.assertEqual(post.text, 'Тестовый текст 2')

    def test_context_create_post(self):
        """Тест контекста формы при создании поста"""
        response = self.authorize_client.get(reverse(
            'posts:post_create'
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        form = response.context['form']
        for field, value in form_fields.items():
            with self.subTest(field=field):
                self.assertIsInstance(form.fields[field], value)

    def test_context_is_edit_post(self):
        """Тест проверки передачи аргумента is_edit в post_edit"""
        response = self.authorize_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': '4'}
        ))
        form = response.context['is_edit']
        self.assertEqual(form, True)

    def test_context_edit_post(self):
        """Проверяет, что в контексте форма вызванного поста"""
        response = self.authorize_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '10'})
        )
        form = response.context['post']
        form_fields = {
            form.text: 'Тестовый текст 6',
            form.author.username: 'roman',
            form.group.slug: 'test_slug'
        }
        for field, value in form_fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, value)
