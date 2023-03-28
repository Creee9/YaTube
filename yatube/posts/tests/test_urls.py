# posts/tests/test_urls.py
from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group
from django.core.cache import cache


User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
        )

        cls.post = Post.objects.create(
            author=cls.author,
            text='Тествоый текст',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_urls_for_all_users(self):
        """Страницы доступные любому пользователю"""
        url_names = [
            '/',
            f'/group/{PostsURLTests.group.slug}/',
            f'/profile/{PostsURLTests.author.username}/',
            f'/posts/{PostsURLTests.post.pk}/',
        ]
        for address in url_names:
            with self.subTest(address=address):
                # Тесты для неавторизованных пользователей
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 (f'Ошибка в url = {address} для guest'))

                # Тесты для авторизованных пользователей
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 (f'Ошибка в url = {address} для authorized'))

    def test_post_create(self):
        """Проверка post_create.
        Aвторизованный redirect to /create/,
        а неавторизованных redirect to /auth/login/
        """
        # Тесты для авторизованных пользователей
        response = self.authorized_client.get('/create/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Ошибка в /create/ для авторизованных'
        )
        # Тесты для неавторизованных пользователей
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response,
            ('/auth/login/?next=/create/'),
            msg_prefix='Ошибка в redirect post_create'
        )

    def test_post_edit(self):
        """Проверка post_create.
        Автор redirect to /post/pk/edit,
        авторизованых to post/pk,
        а неавторизованных redirect to /login/
        """
        author = PostsURLTests.author
        post = PostsURLTests.post
        # для автора
        post_author = Client()
        post_author.force_login(author)
        url = f'/posts/{post.pk}/edit/'
        response = post_author.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'ошибка в post_edit для author')
        # для авторизованных
        response = self.authorized_client.get(url)
        self.assertRedirects(response, (f'/posts/{post.pk}/'),
                             msg_prefix='ошибка в post_edit '
                             'redirect for authorized')
        # для неавторизованных
        # в задании просили направить их на post_detail, а не
        # на /auth/login/
        response = self.guest_client.get(url)
        self.assertRedirects(response,
                             (f'/posts/{post.pk}/'),
                             msg_prefix='ошибка в post_edit '
                             'redirect for guest')

    def test_unexisting_page(self):
        """Страниц не найдена"""
        url = '/some_unexisting_page/'
        clients = {
            'guest': self.guest_client,
            'authorized': self.authorized_client
        }
        for client in clients.values():
            with self.subTest(client=client):
                response = client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.NOT_FOUND,
                    msg='mistake django find page that doesnt exist'
                )

    def test_urls_users_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        group = PostsURLTests.group
        author = PostsURLTests.author
        post = PostsURLTests.post
        post_author = Client()
        post_author.force_login(author)
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{group.slug}/': 'posts/group_list.html',
            f'/profile/{author.username}/': 'posts/profile.html',
            f'/posts/{post.pk}/': 'posts/post_detail.html',
            f'/posts/{post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = post_author.get(path=address)
                self.assertTemplateUsed(response, template)

# для неавторизованных в post/edit
    # response = self.guest_client.get(url)
    # self.assertRedirects(response,
    # (f'/auth/login/?next=/posts/{post.pk}/edit/'),
    # msg_prefix='ошибка в post_edit ''redirect for guest')
