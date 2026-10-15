from django.conf import settings
from django.db import models

from courses.models import Course


class LevelTest(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="level_tests",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    passing_score = models.PositiveSmallIntegerField(default=60)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class LevelTestQuestion(models.Model):
    level_test = models.ForeignKey(
        LevelTest,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    question = models.CharField(max_length=300)
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200, blank=True)
    option_d = models.CharField(max_length=200, blank=True)
    correct_option = models.CharField(max_length=1, default="A")

    def __str__(self):
        return self.question


class LevelTestAttempt(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="level_test_attempts",
    )
    level_test = models.ForeignKey(
        LevelTest,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    score = models.PositiveSmallIntegerField(default=0)
    passed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.student.username} — {self.level_test.title}"
