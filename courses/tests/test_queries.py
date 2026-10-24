from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Max, Min
from django.test import TestCase

from academies.models import Academy
from courses.models import Category, Convocatoria, Course, CourseStatus

User = get_user_model()


class CourseQueriesTests(TestCase):

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
            course = Course.objects.create(
                academy=self.academy,
                category=self.category,
                title=f"Curso {i}",
                slug=f"curso-{i}",
                description="...",
                status=CourseStatus.PUBLISHED,
            )
            Convocatoria.objects.create(
                course=course,
                start_date="2026-07-01",
                end_date="2026-09-30",
                price=Decimal("480.00"),
                total_places=15,
            )

    def test_courses_count_by_category(self):
        result = Category.objects.annotate(
            courses_count=Count("courses"),
        ).get(pk=self.category.pk)
        self.assertEqual(result.courses_count, 3)

    def test_courses_count_by_academy(self):
        result = Academy.objects.annotate(
            courses_count=Count("courses"),
        ).get(pk=self.academy.pk)
        self.assertEqual(result.courses_count, 3)

    def test_convocatoria_avg_price_aggregate(self):
        result = Convocatoria.objects.aggregate(
            avg=Avg("price"),
        )
        self.assertEqual(result["avg"], Decimal("480.00"))

    def test_convocatoria_price_range_aggregate(self):
        result = Convocatoria.objects.aggregate(
            min_price=Min("price"),
            max_price=Max("price"),
        )
        self.assertEqual(result["min_price"], Decimal("480.00"))
        self.assertEqual(result["max_price"], Decimal("480.00"))