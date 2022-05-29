from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма поста: текст, группа и картинка."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст',
            'group': 'Группа'
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост'
        }

    def validate_not_empty(self):
        """Проверка заполнения поля [текст]"""
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError(
                'Введите текст поста!'
            )
        return data


class CommentForm(forms.ModelForm):
    """Форма комментария: текст."""

    class Meta:
        model = Comment
        fields = ('text',)

    def validate_not_empty(self):
        """Проверка заполнения поля [текст]"""
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError(
                'Введите текст комментария!'
            )
        return data
