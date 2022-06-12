import shutil
import tempfile

from django import forms
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..forms import PostForm
from ..models import Post, Group, Comment


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='вторая группа',
            slug='another-slug',
            description='Yet another description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
            group=cls.group
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверка редиректа
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'auth'}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Беру самый "свежий" пост
        first_object = Post.objects.all().order_by('-pub_date')[0]
        # Проверяю содержимое самого свежего поста
        self.assertEqual(first_object.text, 'Тестовый текст')
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.image, 'posts/small.gif')

    def test_add_comment(self):
        """Валидная форма создает комментарий к посту."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }

        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        # Проверка редиректа
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}))
        # Проверяем, увеличилось ли число комментов
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        # Проверяю содержимое самого свежего коммента
        first_object = Comment.objects.all().order_by('-pub_date')[0]
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.text, 'Тестовый комментарий')

    def test_post_edit(self):
        """Тестирование редактирования поста."""
        posts_count = Post.objects.count()

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='image.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Новый текст поста',
            'group': self.group2.id,
            'image': uploaded
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        # Проверка редиректа
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}))
        # Убедимся, что запись в базе данных не создалась
        self.assertEqual(Post.objects.count(), posts_count)
        # Беру пост по id
        post = Post.objects.get(id=self.post.id)
        # Проверяю в нем все, что поменял
        self.assertEqual(post.text, 'Новый текст поста')
        self.assertEqual(post.group, self.group2)
        self.assertEqual(post.image, 'posts/image.gif')

    def test_title_label(self):
        text_label = PostFormTests.form.fields['text'].label
        self.assertEqual(text_label, 'Текст')

        group_label = PostFormTests.form.fields['group'].label
        self.assertEqual(group_label, 'Группа')

    def test_title_help_text(self):
        text_help = PostFormTests.form.fields['text'].help_text
        self.assertEqual(text_help, 'Текст нового поста')

        group_help = PostFormTests.form.fields['group'].help_text
        self.assertEqual(group_help, 'Группа, к которой будет относиться пост')

    def test_create_post_show_correct_context1(self):
        """Проверка полей формы создания поста."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context1(self):
        """Проверка полей формы редактирования поста."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)
