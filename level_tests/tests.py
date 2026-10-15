from django.contrib.auth import get_user_model
from core.test_base import VerboseTestCase
from django.urls import reverse

User = get_user_model()


class LevelTestTests(VerboseTestCase):
    def test_list_is_public(self):
        response = self.client.get(reverse("level_tests:list"))
        self.assertEqual(response.status_code, 200)

    def test_create_requires_academy(self):
        student = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.client.force_login(student)
        response = self.client.get(reverse("level_tests:create"))
        self.assertEqual(response.status_code, 403)
