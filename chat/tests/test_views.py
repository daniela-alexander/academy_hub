from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from chat.models import Conversation, Participant
from chat.services import create_direct_conversation

User = get_user_model()


class ChatWebViewTests(TestCase):

    def setUp(self):
        self.student = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.teacher = User.objects.create_user(
            username="profesor",
            email="profesor@example.com",
            password="TestPassword123!",
            is_academy=True,
        )
        self.conv = create_direct_conversation(self.student, self.teacher)

    def test_list_requires_login(self):
        response = self.client.get(reverse("chat:list"))
        self.assertEqual(response.status_code, 302)

    def test_list_shows_conversations(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("chat:list"))
        self.assertEqual(response.status_code, 200)

    def test_detail_requires_participant(self):
        intruder = User.objects.create_user(
            username="intruso",
            email="intruso@example.com",
            password="TestPassword123!",
        )
        self.client.force_login(intruder)
        response = self.client.get(reverse("chat:detail", kwargs={"pk": self.conv.pk}))
        self.assertEqual(response.status_code, 403)

    def test_detail_shows_messages(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("chat:detail", kwargs={"pk": self.conv.pk}))
        self.assertEqual(response.status_code, 200)

    def test_post_sends_message(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("chat:detail", kwargs={"pk": self.conv.pk}),
            {"text": "Hola"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.conv.messages.count(), 1)
