from django.urls import path

from . import views

app_name = 'posts'

# Добавляем имена путям из приложения posts.
urlpatterns = [
    path('', views.index, name='posts_list'),
    path('group/<slug:slug>/',
         views.group_posts,
         name='group_list'),
    # Просмотр профиля
    path('profile/<str:username>/',
         views.profile,
         name='profile'),
    # Просмотр поста
    path('posts/<int:post_id>/',
         views.post_detail,
         name='post_detail'),
    # Создание поста
    path('create/',
         views.post_create,
         name='post_create'),
    # Редактирование поста
    path('posts/<post_id>/edit/',
         views.post_edit,
         name='post_edit'),
    # Комментирование поста
    path('posts/<int:post_id>/comment/',
         views.add_comment,
         name='add_comment'),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]
