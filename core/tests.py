from django.urls import reverse

from core.test_base import VerboseTestCase
from .models import ContactMessage


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

class ContactMessageModelTests(VerboseTestCase):

    def test_create_contact_message(self):
        message = ContactMessage.objects.create(
            name="Laura",
            email="laura@example.com",
            subject="Consulta",
            message="Hola, quiero información sobre cursos.",
        )

        self.assertEqual(message.name, "Laura")
        self.assertEqual(message.subject, "Consulta")
        self.assertFalse(message.is_read)

    def test_contact_message_string_representation(self):
        message = ContactMessage.objects.create(
            name="Laura",
            email="laura@example.com",
            subject="Consulta",
            message="Hola",
        )

        self.assertEqual(str(message), "Consulta — Laura")