from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from enrollments.models import Enrollment


class Discount(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "Porcentaje"
        FIXED = "fixed", "Importe fijo"

    code = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=200, blank=True)
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE,
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(value__gte=0),
                name="discount_value_gte_zero",
            ),
        ]

    def __str__(self):
        return f"{self.code} ({self.value})"


class Scholarship(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Solicitada"
        APPROVED = "approved", "Aprobada"
        REJECTED = "rejected", "Rechazada"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="scholarships",
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="scholarships",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    reason = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_scholarships",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gte=0),
                name="payment_amount_gte_zero",
            ),
        ]   


    def __str__(self):
        return f"Beca {self.student.username} — {self.status}"


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        PAID = "paid", "Pagado"
        FAILED = "failed", "Fallido"
        REFUNDED = "refunded", "Reembolsado"

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    discount = models.ForeignKey(
        Discount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    reference = models.CharField(max_length=80, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["enrollment", "status"]),
            models.Index(fields=["status"]),
        ]
    def __str__(self):
        return f"Pago {self.enrollment.pk} — {self.amount} ({self.status})"
