from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]
    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError(
                "Ya existe un usuario con este email."
            )
        return email.lower()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "avatar",
            "city",
            "bio",
            "phone",
        ]
    def clean_email(self):
        email = self.cleaned_data["email"]
        queryset = User.objects.filter(
            email__iexact=email
        )
        if self.instance.pk:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )
        if queryset.exists():
            raise forms.ValidationError(
                "Este email ya está siendo utilizado."
            )
        return email.lower()