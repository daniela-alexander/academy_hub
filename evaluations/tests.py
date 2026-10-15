from django.contrib.auth import get_user_model
from core.test_base import VerboseTestCase
from django.urls import reverse

User = get_user_model()


class EvaluationTests(VerboseTestCase):
    def test_academy_can_see_evaluations(self):
        academy = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="TestPassword123!",
            is_academy=True,
        )
        self.client.force_login(academy)
        response = self.client.get(reverse("evaluations:list"))
        self.assertEqual(response.status_code, 200)

    def test_student_cannot_see_evaluations(self):
        student = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.client.force_login(student)
        response = self.client.get(reverse("evaluations:list"))
        self.assertEqual(response.status_code, 403)
