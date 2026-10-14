from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Academy(models.Model):
    """
    Modelo para las academias que publican cursos en Academy Hub.
    Cada academia pertenece a un User con is_academy=True.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="academies",
        verbose_name="Propietarios"
    )

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Nombre",
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
        blank=True,
        verbose_name="Slug"
    )

    description = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="Descripción",
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ciudad",
    )

    address = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Dirección",
    )

    website = models.URLField(
        blank=True,
        verbose_name="Sitio web",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono",
    )

    email = models.EmailField(
        blank=True,
        verbose_name="Email de contacto",
    )

    logo = models.ImageField(
        upload_to="academies/logos/",
        blank=True,
        null=True,
        verbose_name="Logo"
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name="Verificada",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Activa",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    class Meta:
        verbose_name = "Academia"
        verbose_name_plural = "Academias"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_verified"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    """
    Profesor que imparte cursos en una academia
    """

    academy = models.ForeignKey(
        Academy,
        on_delete=models.CASCADE,
        related_name="teachers",
        verbose_name="Academia",
    )

    first_name = models.CharField(
        max_length=100,
        verbose_name="Nombre",
    )

    last_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Apellidos",
    )

    email = models.EmailField(
        blank=True,
        verbose_name="Email",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono",
    )

    specialty = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Especialidad",
    )

    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="Biografía",
    )

    photo = models.ImageField(
        upload_to="teachers/",
        blank=True,
        null=True,
        verbose_name="Foto",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    class Meta:
        verbose_name = "Profesor"
        verbose_name_plural = "Profesores"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["academy"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()
