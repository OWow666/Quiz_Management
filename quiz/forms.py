from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label='电子邮箱')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': '用户名',
            'email': '电子邮箱',
            'password1': '密码',
            'password2': '确认密码',
        }