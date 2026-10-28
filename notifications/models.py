from django.conf import settings
from django.db import models


class Notification(models.Model):

    class Type(models.TextChoices):
        INFO = "info", "Información"
        WARNING = "warning", "Aviso"
        SUCCESS = "success", "Éxito"
        REMINDER = "reminder", "Recordatorio"
        NEW_MESSAGE = "new_message", "Nuevo mensaje de chat"
        ENROLLMENT_RECEIVED = "enrollment_received", "Solicitud de inscripción"
        ENROLLMENT_APPROVED = "enrollment_approved", "Inscripción aprobada"
        ENROLLMENT_REJECTED = "enrollment_rejected", "Inscripción rechazada"
        SCHOLARSHIP_APPROVED = "scholarship_approved", "Beca aprobada"
        SCHOLARSHIP_REJECTED = "scholarship_rejected", "Beca rechazada"
        COURSE_PUBLISHED = "course_published", "Curso publicado"
        SYSTEM = "system", "Aviso del sistema"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    type = models.CharField(
        max_length=30,
        choices=Type.choices,
        default=Type.INFO,
    )

    title = models.CharField(max_length=200)
    message = models.TextField()
    url = models.CharField(max_length=300, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["user", "is_read", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} — {self.title}"
