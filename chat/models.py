from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models

from courses.models import Course


class Conversation(models.Model):
    """
    Conversación entre dos o más usuarios.
    - is_group=False: chat directo (2 participantes).
    - is_group=True: chat grupal creado por un profesor o una academia.
    - course: opcional, ancla la conversación a un curso.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_conversations",
    )

    title = models.CharField(
        max_length=150,
        blank=True,
        help_text="Obligatorio para grupos. Ej: 'Alumnos de Inglés B2'.",
    )

    is_group = models.BooleanField(
        default=False,
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversations",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["-updated_at"]),
            models.Index(fields=["is_group"]),
        ]

    def __str__(self):
        if self.is_group:
            return f"Grupo: {self.title or self.pk}"
        return f"Chat #{self.pk}"

    @property
    def display_title(self):
        if self.is_group:
            return self.title or f"Grupo #{self.pk}"
        return f"Chat #{self.pk}"


class ParticipantRole(models.TextChoices):
    STUDENT = "student", "Alumno"
    TEACHER = "teacher", "Profesor"
    ACADEMY = "academy", "Academia"


class Participant(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="participants",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_participations",
    )

    role = models.CharField(
        max_length=20,
        choices=ParticipantRole.choices,
        default=ParticipantRole.STUDENT,
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["joined_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["conversation", "user"],
                name="unique_participant_per_conversation",
            ),
        ]
        indexes = [
            models.Index(fields=["conversation", "user"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.user.username} en {self.conversation_id}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_chat_messages",
    )

    text = models.TextField(
        max_length=1000,
    )

    is_read = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
            models.Index(fields=["conversation", "is_read"]),
        ]

    def __str__(self):
        return f"{self.sender.username}: {self.text[:40]}"
