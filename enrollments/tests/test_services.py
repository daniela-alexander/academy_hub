from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from academies.models import Academy
from courses.models import Category, Convocatoria, Course, CourseStatus
from enrollments.models import Enrollment, EnrollmentStatus
from enrollments.services import reserve_place

User = get_user_model()


class ReservePlaceTests(TestCase):

    def setUp(self):
        self.academy_user = User.objects.create_user(
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
        self.other_student = User.objects.create_user(
            username="carlos",
            email="carlos@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.academy = Academy.objects.create(
            owner=self.academy_user,
            name="English Now",
            slug="english-now",
        )
        self.category = Category.objects.create(
            name="Idiomas",
            slug="idiomas",
        )
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
            name="Plaza única",
            start_date="2026-07-01",
            end_date="2026-09-30",
            price=Decimal("480.00"),
            total_places=1,
            reserved_places=0,
            enrolled_places=0,
        )

    def test_student_can_reserve_place(self):
        enrollment = reserve_place(self.student, self.convocatoria.pk)
        self.assertEqual(enrollment.status, EnrollmentStatus.RESERVED)
        self.convocatoria.refresh_from_db()
        self.assertEqual(self.convocatoria.reserved_places, 1)

    def test_student_cannot_reserve_twice(self):
        reserve_place(self.student, self.convocatoria.pk)
        with self.assertRaises(ValueError):
            reserve_place(self.student, self.convocatoria.pk)

    def test_student_cannot_reserve_when_full(self):
        print(f"ANTES: reserved_places={self.convocatoria.reserved_places}, is_full={self.convocatoria.is_full}")

        reserve_place(self.other_student, self.convocatoria.pk)

        self.convocatoria.refresh_from_db()
        self.assertTrue(self.convocatoria.is_full) 
        print(f"DESPUÉS: reserved_places={self.convocatoria.reserved_places}, is_full={self.convocatoria.is_full}")

        with self.assertRaises(ValueError):
            reserve_place(self.student, self.convocatoria.pk)

    def test_cannot_reserve_in_inactive_convocatoria(self):
        self.convocatoria.is_active = False
        self.convocatoria.save()
        with self.assertRaises(ValueError):
            reserve_place(self.student, self.convocatoria.pk)