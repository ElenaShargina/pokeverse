# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, PasswordResetForm
from .models import CustomUser
from django.contrib.auth.mixins import LoginRequiredMixin

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email',)

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields

class CustomUserChangePasswordForm(LoginRequiredMixin, PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = PasswordChangeForm.base_fields
        labels = {
            'old_password':'Старый пароль',
            'new_password1':'Новый пароль',
            'new_password2':'Повтор нового пароля'
        }

class CustomUserResetPasswordForm(PasswordResetForm):
    class Meta:
        model = CustomUser
