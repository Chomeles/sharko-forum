from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Post


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=False, help_text="Optional — only used for password resets."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class ThreadForm(forms.Form):
    title = forms.CharField(max_length=200)
    body = forms.CharField(
        max_length=20000,
        widget=forms.Textarea(attrs={"rows": 8, "placeholder": "Write your post…"}),
    )


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 6, "placeholder": "Write a reply…"})
        }
