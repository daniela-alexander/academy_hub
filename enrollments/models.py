from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone

from courses.models import Convocatoria


class EnrollmentStatus(models.TextChoices):
    PENDING = "pending", "Solicitud pendiente"
    APPROVED = "approved", "Admitido"
    REJECTED = "rejected", "Rechazado"
    RESERVED = "reserved", "Reserva activa"
    RESERVATION_EXPIRED = "reservation_expired", "Reserva caducada"
    ENROLLED = "enrolled", "Matriculado"
    WAITLIST = "waitlist", "Lista de espera"
    CANCELLED = "cancelled", "Cancelado"
    COMPLETED = "completed", "Completado"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pendiente"
    PARTIAL = "partial", "Pago parcial"
    PAID = "paid", "Pagado"
    REFUNDED = "refunded", "Reembolsado"
    FAILED = "failed", "Fallido"


class Enrollment(models.Model):
    """
    Solicitud / reserva / matrícula de un alumno en una convocatoria.
    """

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Alumno",
    )

    convocatoria = models.ForeignKey(
        Convocatoria,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Convocatoria",
    )

    status = models.CharField(
        max_length=30,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.PENDING,
        verbose_name="Estado",
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name="Estado de pago",
    )

    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Importe pagado",
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Descuento aplicado",
    )

    reservation_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="La reserva caduca el",
    )

    enrolled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de matrícula",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de finalización",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Notas internas",
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
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "convocatoria"],
                name="unique_student_convocatoria",
            ),
        ]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["payment_status"]),
            models.Index(fields=["student", "status"]),
            models.Index(fields=["convocatoria", "status"]),
        ]

    def __str__(self):
        return f"{self.student.username} → {self.convocatoria}"

    @property
    def is_active(self):
        return self.status in [
            EnrollmentStatus.PENDING,
            EnrollmentStatus.APPROVED,
            EnrollmentStatus.RESERVED,
            EnrollmentStatus.ENROLLED,
            EnrollmentStatus.WAITLIST,
        ]

    @property
    def is_reservation_expired(self):
        if not self.reservation_expires_at:
            return False
        return timezone.now() > self.reservation_expires_at

    @property
    def total_price(self):
        return self.convocatoria.price - self.discount_amount

    @property
    def pending_amount(self):
        return max(self.total_price - self.amount_paid, 0)

class WaitlistEntry(models.Model):
    """
    Entrada en lista de espera para una convocatoria llena.
    """

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="waitlist_entries",
        verbose_name="Alumno",
    )

    convocatoria = models.ForeignKey(
        Convocatoria,
        on_delete=models.CASCADE,
        related_name="waitlist_entries",
        verbose_name="Convocatoria",
    )

    position = models.PositiveIntegerField(
        default=0,
        verbose_name="Posición",
    )

    is_notified = models.BooleanField(
        default=False,
        verbose_name="Notificado",
    )

    notified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de notificación",
    )

    converted_to_enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="waitlist_source",
        verbose_name="Inscripción generada",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de alta en lista",
    )

    class Meta:
        verbose_name = "Lista de espera"
        verbose_name_plural = "Listas de espera"
        ordering = ["position", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "convocatoria"],
                name="unique_waitlist_student_convocatoria",
            ),
        ]
        indexes = [
            models.Index(fields=["convocatoria", "position"]),
        ]

    def __str__(self):
        return f"#{self.position} {self.student.username} → {self.convocatoria}"

class EnrollmentAnswer(models.Model):
    """
    Respuesta del alumno a una pregunta del formulario de inscripción.
    """

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Inscripción",
    )

    question_key = models.CharField(
        max_length=100,
        verbose_name="Clave de la pregunta",
    )

    question_text = models.CharField(
        max_length=300,
        verbose_name="Texto de la pregunta",
    )

    answer_text = models.TextField(
        blank=True,
        verbose_name="Respuesta",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de respuesta",
    )

    class Meta:
        verbose_name = "Respuesta de inscripción"
        verbose_name_plural = "Respuestas de inscripción"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["enrollment"]),
        ]

    def __str__(self):
        return f"{self.question_key}: {self.answer_text[:40]}"

class EnrollmentDocument(models.Model):
    """
    Documento adjunto a una inscripción.
    """

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Inscripción",
    )

    name = models.CharField(
        max_length=150,
        verbose_name="Nombre del documento",
    )

    file = models.FileField(
        upload_to="enrollments/documents/",
        verbose_name="Archivo",
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name="Verificado",
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de subida",
    )

    class Meta:
        verbose_name = "Documento de inscripción"
        verbose_name_plural = "Documentos de inscripción"
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"{self.name} ({self.enrollment})"

