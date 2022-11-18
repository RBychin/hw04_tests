from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from ..models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='Roman'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_main_and_group_status(self):
        """Тест проверки доступа: posts:index, posts:group_list"""
        urls = (
            '/',
            '/group/test_slug/',
        )
        for address in urls:
            with self.subTest():
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_for_authorized(self):
        """Тест проверки доступа: posts:create_post."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_url(self):
        """Тест проверки доступа: posts:create_post, admin"""
        urls = (
            '/create/',
            '/admin/',
        )
        for address in urls:
            with self.subTest():
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_templates(self):
        """Тест соответствия шаблонов URL-ам."""
        templates_urls = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test_slug/',
            'posts/create_post.html': '/create/',
        }
        for template, address in templates_urls.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        """Тест о выдаче ошибки при обращении к неописанному url"""
        response = self.guest_client.get('/tru-la-la/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
