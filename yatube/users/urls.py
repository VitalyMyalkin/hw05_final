from django.contrib.auth.views import LogoutView, LoginView, \
    PasswordResetView, PasswordChangeView, PasswordChangeDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView, PasswordResetDoneView

from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_change/',
        PasswordChangeView.as_view(
            template_name='password_сhange_form.html'
        ),
        name='password_change'
    ),
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(
            template_name='password_сhange_done.html'
        )
    ),
    path(
        'password_reset/',
        PasswordResetView.as_view(
            template_name='password_reset_form.html'
        )
    ),
    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'
        )
    ),
    path(
        '/reset/<uid64>/<token>',
        PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html'
        )
    ),
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(
            template_name='password_reset_complete.html'
        )
    )
]
