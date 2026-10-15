from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from academies.models import Academy
from courses.models import Course


class CourseReview(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_reviews",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course_review",
            ),
        ]
        indexes = [
            models.Index(fields=["course"]),
            models.Index(fields=["student"]),
        ]

    def __str__(self):
        return f"{self.student.username} → {self.course.title} ({self.rating}/5)"


class AcademyReview(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="academy_reviews",
    )
    academy = models.ForeignKey(
        Academy,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "academy"],
                name="unique_student_academy_review",
            ),
        ]
        indexes = [
            models.Index(fields=["academy"]),
            models.Index(fields=["student"]),
        ]

    def __str__(self):
        return f"{self.student.username} → {self.academy.name} ({self.rating}/5)"
