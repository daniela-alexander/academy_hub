from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from chat.services import create_direct_conversation

User = get_user_model()


class ChatAPITests(APITestCase):

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

    def test_list_requires_auth(self):
        response = self.client.get("/api/v1/conversations/")
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_list_shows_conversations(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/v1/conversations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_direct(self):
        other = User.objects.create_user(
            username="carlos",
            email="carlos@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            "/api/v1/conversations/create_direct/",
            {"username": "carlos"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_send_message(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            f"/api/v1/conversations/{self.conv.pk}/send/",
            {"text": "Hola"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_mark_read(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(
            f"/api/v1/conversations/{self.conv.pk}/mark_read/",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
