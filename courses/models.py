from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator


class Category(models.Model):
    """
    Categoría de curso (Idiomas, Informática, Oposiciones...).
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre",
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        verbose_name="Slug",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Icono",
        help_text="Nombre del icono (ej: book, code, music)",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Activa",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class CourseLevel(models.TextChoices):
    BEGINNER = "beginner", "Básico"
    INTERMEDIATE = "intermediate", "Intermedio"
    ADVANCED = "advanced", "Avanzado"
    EXPERT = "expert", "Experto"


class CourseModality(models.TextChoices):
    PRESENCIAL = "presencial", "Presencial"
    ONLINE = "online", "Online"
    HYBRID = "hybrid", "Híbrida"


class CourseStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    PUBLISHED = "published", "Publicado"
    ARCHIVED = "archived", "Archivado"


class EnrollmentMode(models.TextChoices):
    DIRECT = "direct", "Inscripción directa"
    APPROVAL = "approval", "Admisión previa"


class Course(models.Model):
    """
    Curso ofertado por una academia.
    """

    academy = models.ForeignKey(
        "academies.Academy",
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Academia",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="courses",
        verbose_name="Categoría",
    )

    teacher = models.ForeignKey(
        "academies.Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
        verbose_name="Profesor",
    )

    title = models.CharField(
        max_length=180,
        verbose_name="Título",
    )

    slug = models.SlugField(
        max_length=200,
        blank=True,
        verbose_name="Slug",
    )

    description = models.TextField(
        verbose_name="Descripción",
    )

    objectives = models.TextField(
        blank=True,
        verbose_name="Objetivos",
    )

    competences = models.TextField(
        blank=True,
        verbose_name="Competencias",
        help_text="Competencias que desarrolla el curso",
    )

    requirements = models.TextField(
        blank=True,
        verbose_name="Requisitos previos",
    )

    level = models.CharField(
        max_length=20,
        choices=CourseLevel.choices,
        default=CourseLevel.BEGINNER,
        verbose_name="Nivel",
    )

    modality = models.CharField(
        max_length=20,
        choices=CourseModality.choices,
        default=CourseModality.PRESENCIAL,
        verbose_name="Modalidad",
    )

    status = models.CharField(
        max_length=20,
        choices=CourseStatus.choices,
        default=CourseStatus.DRAFT,
        verbose_name="Estado",
    )

    enrollment_mode = models.CharField(
        max_length=20,
        choices=EnrollmentMode.choices,
        default=EnrollmentMode.DIRECT,
        verbose_name="Modo de inscripción",
    )

    requires_level_test = models.BooleanField(
        default=False,
        verbose_name="Requiere prueba de nivel",
    )

    is_negotiable = models.BooleanField(
        default=False,
        verbose_name="Precio negociable",
    )

    duration_hours = models.PositiveIntegerField(
        default=0,
        verbose_name="Duración (horas)",
    )

    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Visitas",
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
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["level"]),
            models.Index(fields=["modality"]),
            models.Index(fields=["category"]),
            models.Index(fields=["academy"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def primary_image(self):
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        return self.images.first()

    @property
    def is_published(self):
        return self.status == CourseStatus.PUBLISHED

    @property
    def has_convocatorias(self):
        return self.convocatorias.filter(is_active=True).exists()

class CourseImage(models.Model):
    """
    Imagen asociada a un curso.
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Curso",
    )

    image = models.ImageField(
        upload_to="courses/",
        verbose_name="Imagen",
    )

    alt_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Texto alternativo",
    )

    is_primary = models.BooleanField(
        default=False,
        verbose_name="Imagen principal",
    )

    position = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Posición",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )

    class Meta:
        verbose_name = "Imagen de curso"
        verbose_name_plural = "Imágenes de curso"
        ordering = ["position", "created_at"]
        indexes = [
            models.Index(fields=["course", "is_primary"]),
        ]

    def __str__(self):
        return f"Imagen de {self.course.title}"
