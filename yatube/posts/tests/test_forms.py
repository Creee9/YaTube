import shutil
import tempfile

from posts.forms import PostForm
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
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
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_form(self):
        """Валидная форма создает запись в Post"""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
                group=self.group.id,
                image='posts/image.png'
            ).exists()
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_post_form(self):
        """Происходит редактирование поста"""
        form_data = {
            'text': "Новый текст",
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ), data=form_data, follow=True
        )
        editet_post = Post.objects.get(id=self.post.id)
        print(editet_post)
        self.assertEqual(editet_post.text, form_data['text'])
        self.assertEqual(editet_post.id, form_data['group'])
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )

    def test_add_comment(self):
        """Тест добавления комментария.
        Комментировать может только авторизованный"""
        form_data = {
            'post': self.post,
            'author': self.user,
            'text': 'Тестовый комментарий',
        }
        comment_count = Comment.objects.count()
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': (self.post.pk)}),
            data=form_data,
            follow=True,
        )
        response_guest = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': (self.post.pk)}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': (self.post.pk)})
        )
        self.assertRedirects(response_guest,
                             ('/auth/login/?next=/posts/1/comment/'))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(
            text=form_data['text'],
            author=self.user,
        ).exists())
