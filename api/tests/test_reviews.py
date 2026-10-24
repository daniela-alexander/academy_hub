from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from academies.models import Academy
from courses.models import Category, Course
from reviews.models import CourseReview

User = get_user_model()


class ReviewAPITests(APITestCase):

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

    def test_list_is_public(self):
        response = self.client.get("/api/v1/course-reviews/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_can_create(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            "/api/v1/course-reviews/",
            {"course": self.course.pk, "rating": 5, "comment": "Excelente"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_rating_must_be_between_1_and_5(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            "/api/v1/course-reviews/",
            {"course": self.course.pk, "rating": 6, "comment": "..."},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
