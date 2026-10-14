from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Implementamos un usuario personalizado que hereda de la clase AbstractUSer.
    Este puede ser academia o alumno
    """
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
    )

    is_academy = models.BooleanField(
        default=False,
        verbose_name="Es academia",
    )

    is_student = models.BooleanField(
        default=False,
        verbose_name="Es alumno",
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Avatar",
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ciudad",
    )

    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="Biografia",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono",
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name="Verificado",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    birth_date = models.DateField(
    blank=True,
    null=True,
    verbose_name="Fecha de nacimiento"
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["-created_at"]

    def __str__(self):
        return self.username