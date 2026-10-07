from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "is_academy",
            "is_student",
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
            "birth_date",
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

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
    
        if phone and not phone.isdigit():
            raise forms.ValidationError(
                "El teléfono solo puede contener números."
            )
    
        return phone