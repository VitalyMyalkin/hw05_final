from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    """Модель сообществ.

    У сообществ есть название, адрес, описание и пользователь-создатель."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE
    )

    def __str__(self):
        """Дает название на страницах сообществ."""
        return self.title


class Post(models.Model):
    """Модель постов.

    У постов есть текст, картинка, дата публикации, сообщество,
    где пост опубликован, и пользователь-создатель."""

    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts'
    )
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        """Вывод текста поста."""
        return self.text[:15]


class Comment(models.Model):
    """Модель комментариев.

    У комментариев есть текст, пост, к которому относится
    комментарий, дата публикации и пользователь-создатель."""

    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(
        Post,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    def __str__(self):
        """Вывод текста комментария."""
        return self.text


class Follow(models.Model):
    """Модель подписок: автор контента и подписчик."""

    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='following'
    )
