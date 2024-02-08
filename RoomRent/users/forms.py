from django.contrib.auth.forms import UserCreationForm # Django provides form for creating users
from django.contrib.auth.forms import User
from django import forms

class CreateUserForm(UserCreationForm):
    profile_picture = forms.ImageField(required=False)
    class Meta:
        model= User
        fields = ['first_name', 'last_name','username', 'email', 'password1', 'password2',]

