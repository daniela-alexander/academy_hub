from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator


class Category(models.Model):
    """
    Categor├¡a de curso (Idiomas, Inform├ítica, Oposiciones...).
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
        verbose_name="Descripci├│n",
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
        verbose_name="Fecha de creaci├│n",
    )

    class Meta:
        verbose_name = "Categor├¡a"
        verbose_name_plural = "Categor├¡as"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class CourseLevel(models.TextChoices):
    BEGINNER = "beginner", "B├ísico"
    INTERMEDIATE = "intermediate", "Intermedio"
    ADVANCED = "advanced", "Avanzado"
    EXPERT = "expert", "Experto"


class CourseModality(models.TextChoices):
    PRESENCIAL = "presencial", "Presencial"
    ONLINE = "online", "Online"
    HYBRID = "hybrid", "H├¡brida"


class CourseStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    PUBLISHED = "published", "Publicado"
    ARCHIVED = "archived", "Archivado"


class EnrollmentMode(models.TextChoices):
    DIRECT = "direct", "Inscripci├│n directa"
    APPROVAL = "approval", "Admisi├│n previa"


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
        verbose_name="Categor├¡a",
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
        verbose_name="T├¡tulo",
    )

    slug = models.SlugField(
        max_length=200,
        blank=True,
        verbose_name="Slug",
    )

    description = models.TextField(
        verbose_name="Descripci├│n",
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
        verbose_name="Modo de inscripci├│n",
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
        verbose_name="Duraci├│n (horas)",
    )

    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Visitas",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creaci├│n",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="├Ültima actualizaci├│n",
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


        return self.status == CourseStatus.PUBLISHED
  --@property
> --def has_convocatorias(self):
> --    return self.convocatorias.filter(is_active=True).exists()
  ++    @property
> ++    def has_convocatorias(self):
> ++        return self.convocatorias.filter(is_active=True).exists()
  ++
  ++
  ++class CourseModality(models.TextChoices):
  ++    PRESENCIAL = "presencial", "Presencial"
  ++    ONLINE = "online", "Online"
  ++    HYBRID = "hybrid", "H├¡brida"
  ++
  ++
> ++class Convocatoria(models.Model):
  ++    course = models.ForeignKey(
  ++        Course,
  ++        on_delete=models.CASCADE,
> ++        related_name="convocatorias",
  ++        verbose_name="Curso",
  ++    )
  ++    name = models.CharField(
  ++        max_length=150,
  ++        blank=True,
  ++        verbose_name="Nombre",
  ++        help_text="Ej: Verano 2026, Grupo A, Ma├▒anas",
  ++    )
  ++    start_date = models.DateField()
  ++    enrollment_deadline = models.DateField(
  ++        null=True,
  ++        blank=True,
  ++        verbose_name="Fecha l├¡mite de inscripci├│n",
  ++    )
  ++    schedule = models.CharField(
  ++        max_length=200,
  ++        blank=True,
  ++        verbose_name="Horario",
  ++        help_text="Ej: L-X-V 18:00-20:00",
  ++    )
  ++    modality = models.CharField(
  ++        max_length=20,
  ++        choices=CourseModality.choices,
  ++        default=CourseModality.PRESENCIAL,
  ++        verbose_name="Modalidad",
  ++    )
  ++    location = models.CharField(
  ++        max_length=200,
  ++        blank=True,
  ++        verbose_name="Ubicaci├│n",
  ++    )
  ++    price = models.DecimalField(
  ++        max_digits=10,
  ++        decimal_places=2,
  ++        validators=[MinValueValidator(0)],
  ++        verbose_name="Precio",
  ++    )
  ++    deposit = models.DecimalField(
  ++        max_digits=10,
  ++        decimal_places=2,
  ++        default=0,
  ++        validators=[MinValueValidator(0)],
  ++        verbose_name="Se├▒al / Reserva",
  ++        help_text="Cantidad a pagar para reservar plaza",
  ++    )
  ++    total_places = models.PositiveIntegerField(
  ++        default=0,
  ++        verbose_name="Plazas totales",
  ++    )
  ++    reserved_places = models.PositiveIntegerField(
  ++        default=0,
  ++        verbose_name="Plazas reservadas",
  ++    )
  ++    enrolled_places = models.PositiveIntegerField(
  ++        default=0,
  ++        verbose_name="Plazas matriculadas",
  ++    )
  ++    is_active = models.BooleanField(
  ++        default=True,
  ++        verbose_name="Activa",
  ++    )
  ++    created_at = models.DateTimeField(
  ++        auto_now_add=True,
  ++        verbose_name="Fecha de creaci├│n",
  ++    )
  ++    updated_at = models.DateTimeField(
  ++        auto_now=True,
  ++        verbose_name="├Ültima actualizaci├│n",
  ++    )
  ++
  ++    class Meta:
> ++        verbose_name = "Convocatoria"
> ++        verbose_name_plural = "Convocatorias"
  ++        ordering = ["start_date"]
  ++        indexes = [
  ++            models.Index(fields=["start_date"]),
  ++            models.Index(fields=["is_active"]),
  ++            models.Index(fields=["course"]),
  ++        ]
  ++
  ++    def __str__(self):
  ++        label = self.name or f"{self.start_date}"
  ++        return f"{self.course.title} ÔÇö {label}"
  ++
  ++    @property
  ++    def available_places(self):
  ++        used = self.reserved_places + self.enrolled_places
  ++        return max(self.total_places - used, 0)
  ++
  ++    @property
  ++    def is_full(self):
  ++        return self.available_places == 0
  ++
  ++    @property
  ++    def is_open(self):
  ++        from django.utils import timezone
  ++
  ++        if not self.is_active or self.is_full:
  ++            return False
  ++        if (
  ++            self.enrollment_deadline
  ++            and timezone.localdate() > self.enrollment_deadline
  ++        ):
  ++            return False
  ++        return True
    
    class CourseImage(models.Model):
        """




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
        verbose_name="Posici├│n",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creaci├│n",
    )

    class Meta:
        verbose_name = "Imagen de curso"
        verbose_name_plural = "Im├ígenes de curso"
        ordering = ["position", "created_at"]
        indexes = [
            models.Index(fields=["course", "is_primary"]),
        ]

    def __str__(self):
        return f"Imagen de {self.course.title}"
