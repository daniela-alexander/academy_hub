from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from academies.models import Academy
from courses.models import Category, Course

User = get_user_model()


class CourseAPITests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="TestPassword123!",
            is_academy=True,
        )
        self.other = User.objects.create_user(
            username="codeacademy",
            email="info@codeacademy.com",
            password="TestPassword123!",
            is_academy=True,
        )
        self.academy = Academy.objects.create(
            owner=self.owner,
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
            status="published",
        )

    def test_list_is_public(self):
        response = self.client.get("/api/v1/courses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_is_public(self):
        response = self.client.get(f"/api/v1/courses/{self.course.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_cannot_create(self):
        response = self.client.post(
            "/api/v1/courses/",
            {
                "academy": self.academy.pk,
                "category": self.category.pk,
                "title": "Francés B1",
                "description": "...",
            },
            format="json",
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            "/api/v1/courses/",
            {
                "academy": self.academy.pk,
                "category": self.category.pk,
                "title": "Francés B1",
                "description": "...",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_other_user_cannot_patch(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.patch(
            f"/api/v1/courses/{self.course.pk}/",
            {"title": "Hackeado"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_search_works(self):
        response = self.client.get("/api/v1/courses/?search=Inglés")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_filter_by_category(self):
        response = self.client.get(f"/api/v1/courses/?category={self.category.pk}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
