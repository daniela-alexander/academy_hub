from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from core.test_base import VerboseTestCase

from academies.models import Academy
from courses.models import Category, Convocatoria, Course, CourseStatus
from enrollments.models import Enrollment
from payments.models import Discount, Payment, Scholarship

User = get_user_model()


class DiscountModelTests(VerboseTestCase):

    def test_discount_value_cannot_be_negative(self):
        with self.assertRaises(IntegrityError):
            Discount.objects.create(
                code="NEG",
                value=Decimal("-10.00"),
            )


class PaymentModelTests(VerboseTestCase):

    def setUp(self):
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

    def test_payment_amount_cannot_be_negative(self):
        with self.assertRaises(IntegrityError):
            Payment.objects.create(
                enrollment=self.enrollment,
                amount=Decimal("-10.00"),
            )


class ScholarshipModelTests(VerboseTestCase):

    def setUp(self):
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

    def test_scholarship_amount_cannot_be_negative(self):
        with self.assertRaises(IntegrityError):
            Scholarship.objects.create(
                student=self.student,
                enrollment=self.enrollment,
                amount=Decimal("-10.00"),
            )