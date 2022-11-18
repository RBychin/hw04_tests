from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Roman')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись поста'
        )

    def test_models_correct_working_str(self):
        """Проверяем, что __str__ отображается верно."""
        group = PostModelTest.group
        post = PostModelTest.post
        verboses = {
            str(group): 'Тестовая группа',
            str(post): 'Тестовая запись'
        }
        for field, expected in verboses.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_group_slug(self):
        group = PostModelTest.group
        self.assertEqual(group.slug, 'test_group')

    def test_models_working_post_names(self):
        """Проверка verbose имен Post"""
        post = PostModelTest.post
        field_verbose = {
            'text': 'Пост',
            'author': 'Автор',
            'group': 'Группа',
            'pub_date': 'Дата',
        }
        for field, expected in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected
                )

    def test_models_working_group_verboses_names(self):
        """Проверка verbose имен Group"""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Название тематики',
            'slug': 'Slug-ссылка',
            'description': 'Описание',
        }
        for field, expected in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name,
                    expected
                )

    def test_models_post_help_text(self):
        """Проверка help_text Post"""
        post = PostModelTest.post
        verboses = {
            'text': 'Введите текст вашего сообщения.',
            'group': 'Выберите группу, необязательно.',
        }
        for field, expected in verboses.items():

            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected
                )
