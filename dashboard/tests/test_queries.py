from decimal import Decimal

from django.contrib.auth import get_user_model
from core.test_base import VerboseTestCase
from django.urls import reverse

from academies.models import Academy
from courses.models import Category, Convocatoria, Course, CourseStatus
from enrollments.models import Enrollment
from payments.models import Payment
from reviews.models import CourseReview

User = get_user_model()


class DashboardQueriesTests(VerboseTestCase):

    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="TestPassword123!",
            is_staff=True,
        )
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
            status=CourseStatus.PUBLISHED,
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
            status=Payment.Status.PAID,
        )

    def test_dashboard_avg_rating(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.context["avg_rating"], 5)

    def test_dashboard_total_revenue(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.context["total_revenue"], Decimal("100.00"))