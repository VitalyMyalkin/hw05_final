from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse

from ..models import Post, Group, Follow

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # второй авторизованый клиент
        self.user2 = User.objects.create_user(username='igor')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        self.post2 = Post.objects.create(
            author=self.user2,
            text='пост игоря',
        )

    # Проверяем общедоступные страницы
    def test_url_exists_at_desired_location(self):
        """Проверка доступа к страницам для любого пользователя."""
        locations = ('/',
                     '/group/test-slug/',
                     f'/posts/{self.post.id}/',
                     '/profile/auth/'
                     )

        for url in locations:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_exists_at_desired_location(self):
        """Проверка доступа к страницам для авторизованного пользователя."""
        locations = ('/create/', f'/posts/{self.post.id}/edit/',)

        for url in locations:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем редиректы
    def test_create_url_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_follow(self):
        """Тестирование подписки на автора и отписки от него."""
        follows_count = Follow.objects.count()
        response = self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'igor'}))
        # Проверка редиректа
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'igor'}))
        # Проверяем, увеличилось ли число подписок
        self.assertEqual(Follow.objects.count(), follows_count + 1)
        # Проверяю, что создана необходимая нам подписка
        first_object = Follow.objects.all()[0]
        self.assertEqual(first_object.author, self.user2)
        self.assertEqual(first_object.user, self.user)
        # Проверим появление поста игоря в избраннных
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object, self.post2)
        # Теперь отписка
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': 'igor'}))
        # Проверка редиректа
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'igor'}))
        # Проверяем, уменьшилось ли число подписок
        self.assertEqual(Follow.objects.count(), follows_count)
        # Проверим, что поста игоря больше нет в избраннных
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(self.post2, response.context['page_obj'])

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{self.post.id}/edit/': 'create_post.html',
            '/create/': 'create_post.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
