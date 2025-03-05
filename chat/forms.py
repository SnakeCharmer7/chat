from django import forms
from django.contrib.auth.models import User
import re
from .models import *


class ChatmessageCreateForm(forms.ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].label = ""
        self.fields['text'].widget.attrs.update({
            'placeholder': 'Add message ...', 
            'class': 'form-control rounded-start', 
            'autofocus': True
        })


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8, required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['username']
        help_texts = {'username': None}

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        if len(username) >= 20:
            raise forms.ValidationError("Username must contain a maximum of 20 characters.")
        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            raise forms.ValidationError("Username can only contain letters, numbers, underscores, and hyphens.")

        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must contain at least one number.")

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords must be the same.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user