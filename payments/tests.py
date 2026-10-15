from django.contrib.auth import get_user_model
from core.test_base import VerboseTestCase
from django.urls import reverse

from .models import Discount, Scholarship
from reviews.models import CourseReview

User = get_user_model()


class DiscountTests(VerboseTestCase):
    def setUp(self):
        self.academy = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="TestPassword123!",
            is_academy=True,
        )

    def test_academy_can_create_discount(self):
        self.client.force_login(self.academy)
        response = self.client.post(
            reverse("payments:discount_create"),
            {
                "code": "VERANO10",
                "discount_type": "percentage",
                "value": 10,
                "is_active": True,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Discount.objects.count(), 1)

    def test_student_cannot_create_discount(self):
        student = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.client.force_login(student)
        response = self.client.get(reverse("payments:discount_create"))
        self.assertEqual(response.status_code, 403)


def test_my_reviews_filter_by_rating(self):
    self.client.force_login(self.student)
    CourseReview.objects.create(
        student=self.student, course=self.course, rating=5,
    )
    CourseReview.objects.create(
        student=self.student, course=self.course2, rating=2,
    )
    response = self.client.get(
        reverse("reviews:mine"),
        {"rating": "5"},
    )
    self.assertContains(response, "5/5")