from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from academies.models import Academy
from courses.models import Category, Convocatoria, Course

User = get_user_model()


class EnrollmentAPITests(APITestCase):

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
        self.academy = Academy.objects.create(
            owner=self.academy_user,
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
            name="Verano",
            start_date="2026-07-01",
            end_date="2026-09-30",
            price=Decimal("480.00"),
            total_places=15,
        )

    def test_student_can_create_enrollment(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            "/api/v1/enrollments/",
            {"convocatoria": self.convocatoria.pk},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_anonymous_cannot_create(self):
        response = self.client.post(
            "/api/v1/enrollments/",
            {"convocatoria": self.convocatoria.pk},
            format="json",
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_mine_returns_own(self):
        self.client.force_authenticate(user=self.student)
        self.client.post(
            "/api/v1/enrollments/",
            {"convocatoria": self.convocatoria.pk},
            format="json",
        )
        response = self.client.get("/api/v1/enrollments/mine/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reserve_via_action(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            f"/api/v1/convocatorias/{self.convocatoria.pk}/reserve/",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
