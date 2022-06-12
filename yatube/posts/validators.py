from django import forms


def validate_not_empty(value):
    """Проверка заполнения поля [текст]"""
    if value == '':
        raise forms.ValidationError(
            'Введите, пожалуйста, текст!'
        )
