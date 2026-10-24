from django.conf import settings
from django.db import models

from enrollments.models import Enrollment


class Evaluation(models.Model):
    class Kind(models.TextChoices):
        INITIAL = "initial", "Inicial"
        FINAL = "final", "Final"

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="evaluations",
    )
    kind = models.CharField(max_length=20, choices=Kind.choices)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    evaluated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evaluations_made",
    )
    evaluated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "kind"],
                name="unique_evaluation_per_enrollment_kind",
            ),
        ]
        indexes = [
            models.Index(fields=["enrollment", "kind"]),
        ]

    def __str__(self):
        return f"{self.enrollment} — {self.kind}"
