from django.test import Client, TestCase


class PostsViewTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()

    def test_pages_uses_correct_template(self):
        """Запрос неизвестной страницы возвращает страницу 404"""
        response = self.authorized_client.get('ra')
        self.assertTemplateUsed(response, 'core/404.html')
