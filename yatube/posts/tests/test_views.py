from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group
from django import forms

User = get_user_model()


class PostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создается 1 пост используемый в тестах с одним автором и
        одной группой, помимо этого создается еще один автор и группа,
        это позволяет нам сделать проверку, что при создании - пост,
        попадает в верную группу с верным автором и не отображается в
        другой выборке. Так же для проверки паджинатора, через bulk_create
        создается еще 13 постов"""

        super().setUpClass()
        Group.objects.bulk_create([
            Group(title='Тестовая группа2',
                  slug='test_slug_2'),
            Group(title='Тестовая группа',
                  slug='test_slug')
        ])
        User.objects.bulk_create([
            User(username='test_user'),
            User(username='roman')
        ])
        cls.another_group = Group.objects.get(slug='test_slug_2')
        cls.another_author = User.objects.get(username='test_user')
        cls.group = Group.objects.get(slug='test_slug')
        cls.user = User.objects.get(username='roman')
        Post.objects.bulk_create([
            Post(text='Тестовый пост.',
                 group=cls.group,
                 author=cls.user,
                 pk=1),
            Post(text='Неиспользуемый тестовый пост.',
                 group=cls.another_group,
                 author=cls.another_author)
        ])
        cls.post = Post.objects.get(pk=1)
        cls.another_post = Post.objects.get(pk=2)
        Post.objects.bulk_create([
            Post(text=f'Пост для паджинатора {i}',
                 group=cls.group,
                 author=cls.user) for i in range(2, 15)
        ])

    def setUp(self):
        self.guest_client = Client()
        self.authorize_client = Client()
        self.authorize_client.force_login(self.user)

    def test_correct_HTML_templates(self):
        """Проверка корректности шаблонов и адресов."""
        templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk}
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
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        for address in addresses:
            response = self.authorize_client.get(address)
            with self.subTest(address=address):
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_paginator_second_page(self):
        """Тестирование второй страницы паджинатора для Главной страницы,
        Страницы группы, Страницы профиля."""
        addresses = (
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
            reverse('posts:index')
        )
        for address in addresses:
            response = self.guest_client.get(
                address + '?page=2'
            )
            with self.subTest(address=address):
                self.assertEqual(
                    len(response.context['page_obj']),
                    5 if address == reverse('posts:index') else 4
                )

    def test_context(self):
        """Тест контекста главной страницы."""
        response = self.authorize_client.get(reverse('posts:index'))
        first_obj = response.context['page_obj'][0]
        context = {
            first_obj.group.title: 'Тестовая группа',
            first_obj.text: 'Пост для паджинатора 14',
            first_obj.author.username: 'roman',
            first_obj.group.slug: 'test_slug'
        }
        for field, value in context.items():
            with self.subTest(context=field):
                self.assertEqual(field, value)

    def test_context_post_detail(self):
        """Тест контекста для post_detail"""
        response = self.authorize_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        ))
        post = response.context['post']
        self.assertEqual(post.text, 'Тестовый пост.')

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

    def test_post_added_correct(self):
        """Проверка: добавленный пост не попадает к в другую группу/к другому
        автору"""
        post_count = Post.objects.filter(group=self.another_group).count()
        post = Post.objects.create(
            text='Еще один пост в другой гурппе с другим автором',
            group=self.another_group,
            author=self.another_author
        )
        response = self.guest_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            )
        )
        self.assertEqual(
            Post.objects.filter(group=self.another_group).count(),
            post_count + 1
        )
        self.assertNotIn(
            post, response.context['page_obj'],
            f'Пост "{post.text}", должен находиться в группе '
            f'{self.another_group}, а находится в {self.group}')

    def test_context_is_edit_post(self):
        """Тест проверки передачи аргумента is_edit в post_edit"""
        response = self.authorize_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}
        ))
        form = response.context['is_edit']
        self.assertEqual(form, True)

    def test_context_edit_post(self):
        """Проверяет, что в контексте форма вызванного поста"""
        response = self.authorize_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form = response.context['post']
        form_fields = {
            form.text: 'Тестовый пост.',
            form.author.username: 'roman',
            form.group.slug: 'test_slug'
        }
        for field, value in form_fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, value)
