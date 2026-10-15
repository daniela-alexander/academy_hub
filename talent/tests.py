from django.contrib.auth import get_user_model
from core.test_base import VerboseTestCase
from django.urls import reverse

User = get_user_model()


class PassportTests(VerboseTestCase):
    def test_student_can_see_own_passport(self):
        student = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.client.force_login(student)
        response = self.client.get(reverse("talent:passport"))
        self.assertEqual(response.status_code, 200)

    def test_competences_require_staff(self):
        student = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.client.force_login(student)
        response = self.client.get(reverse("talent:competence_list"))
        self.assertEqual(response.status_code, 403)
