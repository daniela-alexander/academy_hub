from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_academy = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    city = models.CharField(
        max_length=100,
        blank=True
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    bio = models.TextField(
        max_length=500,
        blank=True,
    )

    is_verified =models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    birth_date = models.DateField(
    blank=True,
    null=True,
    )

    def __str__(self):
        return self.username