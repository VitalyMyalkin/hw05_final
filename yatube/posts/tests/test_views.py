import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..models import Group, Post
from ..forms import PostForm

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
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
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:posts_list'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'auth'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}): 'create_post.html',
            reverse('posts:post_create'): 'create_post.html',
        }

        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_post_show_correct_context(self):
        """Шаблон создания поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertNotIn('is_edit', response.context)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_edit_show_correct_context(self):
        """Шаблон редактирования поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id})
        )
        self.assertTrue(response.context['is_edit'])
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context['post'], self.post)

    def test_index_show_correct_context(self):
        """Шаблон главной сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:posts_list'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object, self.post)

    def test_index_cache_context(self):
        """Тест кеширования главной страницы"""
        post2 = Post.objects.create(
            author=self.user,
            text='пост тест кеша',)

        response = self.client.get(reverse('posts:posts_list'))
        self.assertEqual(len(response.context['page_obj']), 2)
        content = response.content
        post2.delete()
        self.assertEqual(response.content, content)
        cache.clear()
        response = self.client.get(reverse('posts:posts_list'))
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_group_show_correct_context(self):
        """Шаблон группы сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object, self.post)
        self.assertEqual(first_object.group, self.group)
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'another-slug'}))
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_profile_show_correct_context(self):
        """Шаблон профиля сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object, self.post)
        self.assertEqual(first_object.author, self.user)


class PaginatorViewsTest(TestCase):
    """Тест пажинатора для главной, группы и профиля."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PAGINATOR_LIMIT = 10  # Дефолт пажинатора
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.TOTAL_POSTS = 13  # Only from 11 to 20

        posts = []
        for i in range(cls.TOTAL_POSTS):
            posts.append(Post(author=cls.user,
                              text='Тестовая пост' + str(i),
                              group=cls.group,
                              ))
        Post.objects.bulk_create(posts)

    def test_paginator(self):
        templates_page_names = (
            reverse('posts:posts_list'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}))

        for reverse_name in templates_page_names:
            # Проверка: количество постов на первой странице равно 10.
            response = self.client.get(reverse_name)
            self.assertEqual(len(response.context['page_obj']),
                             self.PAGINATOR_LIMIT)
            # Проверка: на второй странице должно быть три поста.
            response = self.client.get(reverse_name + '?page=2')
            # Здесь сделан костыль зависимости от дефолта пажинатора
            self.assertEqual(len(response.context['page_obj']),
                             self.TOTAL_POSTS - self.PAGINATOR_LIMIT)
