from core.test_base import VerboseTestCase
from core.models import ContactMessage



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

