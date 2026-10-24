from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase

from academies.models import Academy
from courses.models import Category, Convocatoria, Course
from dashboard.cache import (
    STATS_KEY,
    get_global_stats,
    invalidate_global_stats,
)
from enrollments.models import Enrollment
from payments.models import Payment
from reviews.models import CourseReview

User = get_user_model()


class GlobalStatsCacheTests(TestCase):

    def setUp(self):
        cache.clear()
        self.owner = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="TestPassword123!",
            is_academy=True,
        )
        self.student = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.academy = Academy.objects.create(
            owner=self.owner,
            name="English Now",
            slug="english-now",
        )
        self.category = Category.objects.create(name="Idiomas", slug="idiomas")
        self.course = Course.objects.create(
            academy=self.academy,
            category=self.category,
            title="Inglés B2",
            slug="ingles-b2",
            description="...",
            status="published",
        )
        self.convocatoria = Convocatoria.objects.create(
            course=self.course,
            start_date="2026-07-01",
            end_date="2026-09-30",
            price=Decimal("480.00"),
            total_places=15,
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )
        CourseReview.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
        )
        Payment.objects.create(
            enrollment=self.enrollment,
            amount=Decimal("100.00"),
            status="paid",
        )

    def tearDown(self):
        cache.clear()

    def test_stats_cache_miss_populates(self):
        self.assertIsNone(cache.get(STATS_KEY))

        stats = get_global_stats()

        self.assertEqual(stats["total_courses"], 1)
        self.assertEqual(stats["total_enrollments"], 1)
        self.assertEqual(stats["total_reviews"], 1)
        self.assertEqual(stats["avg_rating"], 5.0)
        self.assertEqual(stats["total_revenue"], 100.0)
        self.assertIsNotNone(cache.get(STATS_KEY))

    def test_stats_cache_hit_does_not_query(self):
        get_global_stats()

        with self.assertNumQueries(0):
            stats = get_global_stats()

        self.assertEqual(stats["total_courses"], 1)

    def test_invalidate_stats(self):
        get_global_stats()
        self.assertIsNotNone(cache.get(STATS_KEY))

        invalidate_global_stats()
        self.assertIsNone(cache.get(STATS_KEY))