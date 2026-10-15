from django.conf import settings
from django.db import models


class Competence(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        "courses.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="competences",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TalentPassport(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="talent_passport",
    )
    headline = models.CharField(max_length=200, blank=True)
    summary = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pasaporte de {self.student.username}"


class PassportEntry(models.Model):
    passport = models.ForeignKey(
        TalentPassport,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    competence = models.ForeignKey(
        Competence,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    level = models.PositiveSmallIntegerField(default=1)
    evidence = models.TextField(blank=True)
    obtained_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-obtained_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["passport", "competence"],
                name="unique_passport_competence",
            ),
        ]

    def __str__(self):
        return f"{self.passport.student.username} — {self.competence.name}"
