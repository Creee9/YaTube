import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404

from posts.models import Post, Group, Comment, Follow

User = get_user_model()
NUMBER_OF_POSTS: int = 13
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewTests(TestCase):
    @classmethod
    def setUpClass(cls):

        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.image_png = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='image.png',
            content=cls.image_png,
            content_type='image/png'
        )
        for i in range(NUMBER_OF_POSTS):
            Post.objects.create(
                text=f'Тестовый пост {i}',
                author=cls.user,
                group=cls.group,
                image=cls.uploaded,
            )
        cls.posts = Post.objects.all()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):

        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """Во view-функциях используются правильные html-шаблоны"""

        templated_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.posts[1].id}
                    ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.posts[1].id}
                    ): 'posts/create_post.html',
        }
        for reverse_name, template in templated_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        """Cловарь contex соответствует ожиданиям на страницах:
        'posts:index', 'posts:group_list' и 'posts:profile'"""

        templates_url_names = [
            reverse('posts:index'),
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile', kwargs={'username': self.user}
            ),
        ]
        for reverse_name in templates_url_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                self.assertEqual(response.status_code, 200)
                self.assertEqual(first_object.text, self.posts[0].text)
                self.assertEqual(
                    first_object.author.username,
                    self.user.username
                )
                self.assertEqual(first_object.group.title, self.group.title)
                self.assertEqual(first_object.id, self.posts[0].id)
                self.assertEqual(first_object.image, self.posts[0].image)

    def test_post_detail_show_correct_context(self):
        """Cловарь contex соответствует ожиданиям на странице 'post_detail'"""

        response = self.client.get(reverse('posts:post_detail',
                                           args=[self.posts[0].id]))
        first_object = response.context['one_post']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(first_object.text, self.posts[0].text)
        self.assertEqual(first_object.author.username, self.user.username)
        self.assertEqual(first_object.group.title, self.group.title)
        self.assertEqual(first_object.image, self.posts[0].image)

    def test_post_create_show_correct_context(self):
        """Cловарь contex соответствует ожиданиям на странице 'post_create'"""

        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Cловарь contex соответствует ожиданиям на странице 'post_edit'"""

        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      args=[self.posts[1].id]))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_paginator(self):
        """Paginator показывает правильное кол-во постов на страницах
        'posts:index', 'posts:group_list' и 'posts:profile'"""

        templates_url_names = [
            (reverse('posts:index'), 10),
            (reverse('posts:index') + '?page=2', 3),
            (reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ), 10),
            (reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ) + '?page=2', 3),
            (reverse('posts:profile', args={self.user}), 10),
            (reverse('posts:profile', args={self.user}) + '?page=2', 3),
        ]

        for reverse_name, expected_num_posts in templates_url_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(
                    response.context['page_obj']
                ), expected_num_posts)

    def test_post_added_correctly(self):
        """Пост при создании добавлен корректно"""

        post = Post.objects.create(
            text='Тестовый текст проверка как добавился',
            author=self.user,
            group=self.group)
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index, 'поста нет на главной')
        self.assertIn(post, group, 'поста нет в профиле')
        self.assertIn(post, profile, 'поста нет в группе')

    def test_add_comment(self):
        """Комметарий появился на странице поста"""

        comment = Comment.objects.create(
            post=self.posts[0],
            author=self.user,
            text='Тестовый комментарий'
        )
        response_post_detail = self.client.get(reverse(
            'posts:post_detail',
            args=[self.posts[0].id])
        )
        post_detail = response_post_detail.context['comments']
        self.assertIn(comment, post_detail, ' у поста нет комментария')

    def test_index_caches(self):
        """Страница index кешируется"""
        response = self.authorized_client.get(reverse('posts:index'))
        Post.objects.all().delete()
        response1 = self.authorized_client.get(reverse('posts:index'))
        cache.clear()
        response2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response1.content)
        self.assertNotEqual(response1.content, response2.content)


class FollowViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Auth')
        cls.follower = User.objects.create_user(username='Follower')
        cls.following_author = User.objects.create_user(
            username='Following_author'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовое описание поста',
            group=cls.group
        )
        cls.post_2 = Post.objects.create(
            author=cls.user,
            text='Тестовое описание поста 6',
            group=cls.group_2
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.client_follower = Client()
        self.client_follower.force_login(self.follower)
        # self.user = User.objects.create_user(username='User1')
        # self.follow_author = User.objects.create_user(username='User2')
        # self.authorized_client = Client()
        # self.authorized_client.force_login(self.user)
        # self.authorized_client.force_login(self.follow_author)
        # self.post = Post.objects.create(
        #     author=self.user,
        #     text='Тестовое описание поста'
        # )

    def test_follow_index_page(self):
        """Новая запись появляется в ленте тех, кто на него подписан
        И не появляется у тех, кто не подписан"""
        self.client_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.following_author},
            )
        )
        Post.objects.create(
            id=7,
            author=self.following_author,
            text='Тестовое текст 7',
            group=self.group
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.follower},
            )
        )
        Post.objects.create(
            author=self.follower,
            text='Тестовое текст 8',
            group=self.group_2
        )
        follower_response = self.client_follower.get(
            reverse('posts:follow_index')
        )
        first_object = follower_response.context['page_obj'][0]
        self.assertEqual(first_object.author, self.following_author)
        self.assertEqual(first_object.text, 'Тестовое текст 7')
        self.assertEqual(first_object.id, 7)
        non_follower_response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        nf_first_object = non_follower_response.context['page_obj'][0]
        self.assertEqual(nf_first_object.author, self.follower)
        self.assertEqual(nf_first_object.text, 'Тестовое текст 8')
        self.assertEqual(nf_first_object.id, 8)

    def test_authorized_client_can_follow(self):
        '''Проверка может ли подписываться авторизованный
        пользователь на автора.'''
        test_user = User.objects.create_user(username='testovUser')
        response = self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': test_user.username}
            ), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Follow.objects.count(), 1)
        follow = Follow.objects.first()
        self.assertEqual(follow.user, self.user)
        self.assertEqual(follow.author, test_user)

    def test_authorized_client_follow_author(self):
        self.client_follower.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user}
            )
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.follower,
                author=self.user
            ).exists()
        )

    def test_authorized_client_unfollow_author(self):
        '''Авторизованный пользователь может удалять авторов из подписок.'''
        user = self.user
        author = get_object_or_404(User,
                                   username=self.following_author.username)
        if user != author:
            Follow.objects.get_or_create(user=self.user,
                                         author=self.following_author)
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.following_author.username}
        ))
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.following_author
        ).exists())
