from django.contrib import admin

from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    """Админ-модель постов.

    У постов есть текст, дата публикации, сообщество,
    где пост опубликован, и пользователь-создатель."""

    list_display = ('pk',
                    'text',
                    'pub_date',
                    'author',
                    'group')
    # Настроено дополнение постов сообществами напрямую из админ-зоны.
    list_editable = ('group',)
    # Настроен поиск постов по содержанию текста.
    search_fields = ('text',)
    # Настроена фильтрация постов по дате публикации.
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Админ-модель сообществ.

    У сообществ есть название, адрес, описание и пользователь-создатель."""

    list_display = ('title',
                    'slug',
                    'description',
                    'author',
                    )
    # Настроен поиск сообществ по адресам.
    search_fields = ('slug',)
    # Настроена фильтрация сообществ по их названиям.
    list_filter = ('title',)
    empty_value_display = '-пусто-'


# В админ-зоне можно создавать посты.
admin.site.register(Post, PostAdmin)

# В админ-зоне можно создавать сообщества.
admin.site.register(Group, GroupAdmin)
