from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


class AboutTestPack(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_working(self):
        """Проверка доступности страниц about:author и about:tech"""
        urls = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK
        }
        for url, status in urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url).status_code
                self.assertEqual(response, status)
