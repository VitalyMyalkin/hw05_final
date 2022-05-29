from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm

LIMIT: int = 10


def index(request):
    """Создает главную страницу с пажинатором"""
    context = {
        'page_obj': create_pages(request,
                                 Post.objects.all().order_by('-pub_date')),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Страница с постами конкретной группы."""
    group = get_object_or_404(Group, slug=slug)
    context = {
        'group': group,
        'page_obj': create_pages(request,
                                 group.posts.all().order_by('-pub_date'))
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Профиль пользователя."""
    author = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        context = {
            'author': author,
            'page_obj': create_pages(request,
                                     author.posts.all().order_by('-pub_date')),
            'following': Follow.objects.filter(user=request.user,
                                               author=author
                                               ).exists()
        }
    else:
        context = {
            'author': author,
            'page_obj': create_pages(request,
                                     author.posts.all().order_by('-pub_date'))
        }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Страница просмотра поста."""
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post,
        'form': CommentForm(request.POST or None),
        'comments': post.comments.all().order_by('pub_date')
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Cоздание поста."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        context = {
            'form': form
        }
        return render(request, 'create_post.html', context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user)


@login_required
def post_edit(request, post_id):
    """Редактирование поста."""
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(instance=post,
                    files=request.FILES or None,
                    data=request.POST)
    if not form.is_valid():
        context = {
            'form': form,
            'is_edit': True
        }
        return render(request, 'create_post.html', context)
    form.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Страница с постами, на авторов которых подписан текущий пользователь"""
    context = {
        'page_obj': create_pages(
            request,
            Post.objects.filter(
                author__following__user=request.user
            ).all().order_by('-pub_date')),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора"""
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return redirect('posts:profile', username=username)
    Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора"""
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return redirect('posts:profile', username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)


def create_pages(request, post_list):
    """Получение страниц с пажинатором."""
    paginator = Paginator(post_list, LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
