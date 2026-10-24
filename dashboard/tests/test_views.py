from django.contrib.auth import get_user_model
from core.test_base import VerboseTestCase
from django.urls import reverse

User = get_user_model()


class DashboardTests(VerboseTestCase):
    def test_requires_login(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 302)

    def test_student_sees_student_dashboard(self):
        student = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.client.force_login(student)
        response = self.client.get(reverse("dashboard:home"))
        self.assertTemplateUsed(response, "dashboard/student_dashboard.html")
