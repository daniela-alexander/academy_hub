from django.contrib.auth import get_user_model
from django.db.models import Count
from core.test_base import VerboseTestCase

from academies.models import Academy
from courses.models import Category, Course

User = get_user_model()


class AcademyQueriesTests(VerboseTestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="TestPassword123!",
            is_academy=True,
        )
        self.academy = Academy.objects.create(
            owner=self.user,
            name="English Now",
            slug="english-now",
        )
        self.category = Category.objects.create(
            name="Idiomas",
            slug="idiomas",
        )
        for i in range(3):
            Course.objects.create(
                academy=self.academy,
                category=self.category,
                title=f"Curso {i}",
                slug=f"curso-{i}",
                description="...",
            )

    def test_academy_courses_count_annotation(self):
        result = Academy.objects.annotate(
            courses_count=Count("courses"),
        ).get(pk=self.academy.pk)
        self.assertEqual(result.courses_count, 3)

    def test_academy_teachers_count_annotation(self):
        result = Academy.objects.annotate(
            teachers_count=Count("teachers"),
        ).get(pk=self.academy.pk)
        self.assertEqual(result.teachers_count, 0)