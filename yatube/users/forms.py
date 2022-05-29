from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import get_user_model

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


"""class ChangePasswordForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('current_password', 'new_password', 'new_password_confirm')

class ResetPasswordForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('new_password', 'new_password_confirm')"""
