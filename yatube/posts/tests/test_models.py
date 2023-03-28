from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()

CHAR_COUNT = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='12345678901234567890',
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        # field_str = {
        #     PostModelTest.group.__str__: 'Тестовая группа',
        #     PostModelTest.post.__str__: '123456789012345',
        # }
        # for field, value in field_str.items():
        #     with self.subTest(value=value):
        #         self.assertEqual(
        #             field(), value
        #         )
        post = PostModelTest.post
        expected_text = post.text[:CHAR_COUNT]
        self.assertEqual(str(self.post), expected_text)

        group = PostModelTest.group
        expected_title = group.title
        self.assertEqual(str(self.group), expected_title)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относится пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
