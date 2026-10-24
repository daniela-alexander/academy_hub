from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):

    def test_register_creates_user(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "laura",
                "email": "laura@example.com",
                "password": "TestPassword123!",
                "is_student": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="laura").exists())

    def test_login_returns_user(self):
        User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
        )
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "laura", "password": "TestPassword123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "laura")

    def test_me_requires_auth(self):
        response = self.client.get("/api/v1/auth/me/")
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_me_returns_user_when_authenticated(self):
        user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
        )
        self.client.force_authenticate(user=user)
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "laura")
        self.assertNotIn("email", response.data)
        self.assertNotIn("phone", response.data)
