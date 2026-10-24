from django.urls import reverse
from django.contrib.auth import get_user_model

from core.test_base import VerboseTestCase
from core.models import ContactMessage

User = get_user_model()

class ContactMessageViewTests(VerboseTestCase):

    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="TestPassword123!",
            is_staff=True,
        )

    def test_contact_form_is_public(self):
        response = self.client.get(reverse("core:contact"))
        self.assertEqual(response.status_code, 200)

    def test_anyone_can_send_message(self):
        response = self.client.post(
            reverse("core:contact"),
            {
                "name": "Laura",
                "email": "laura@example.com",
                "subject": "Consulta",
                "message": "Hola",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_staff_can_see_messages(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("core:contact_message_list"))
        self.assertEqual(response.status_code, 200)

    def test_non_staff_cannot_see_messages(self):
        user = User.objects.create_user(
            username="alumno",
            email="alumno@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("core:contact_message_list"))
        self.assertEqual(response.status_code, 403)


class HomeViewTests(VerboseTestCase):

    def test_home_page_returns_200(self):
        response = self.client.get(
            reverse("core:home")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_home_page_uses_correct_template(self):
        response = self.client.get(
            reverse("core:home")
        )

        self.assertTemplateUsed(
            response,
            "core/home.html",
        )
