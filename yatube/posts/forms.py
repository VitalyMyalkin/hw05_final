from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма поста: текст, группа и картинка."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст',
            'group': 'Группа',
            'image': 'Картинка'
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Прикрепите к посту изображение'
        }


class CommentForm(forms.ModelForm):
    """Форма комментария: текст."""

    class Meta:
        model = Comment
        fields = ('text',)
