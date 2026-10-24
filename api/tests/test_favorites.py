from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from academies.models import Academy
from courses.models import Category, Course, CourseFavorite

User = get_user_model()


class CourseFavoriteAPITests(APITestCase):

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
            status="published",
        )

    def test_student_can_favorite(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            f"/api/v1/courses/{self.course.pk}/favorite/",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CourseFavorite.objects.filter(
                user=self.student,
                course=self.course,
            ).exists()
        )

    def test_owner_cannot_favorite_own_course(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            f"/api/v1/courses/{self.course.pk}/favorite/",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_cannot_favorite(self):
        response = self.client.post(
            f"/api/v1/courses/{self.course.pk}/favorite/",
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )
