from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class RegisterTests(TestCase):
    def test_register_page_returns_200(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)

    def test_user_can_register(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "laura",
                "email": "laura@example.com",
                "first_name": "Laura",
                "last_name": "Garcia",
                "password1": "TestPassword123!",
                "password2": "TestPassword123!",
            },
        )

        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.username, "laura")
        self.assertTrue(user.check_password("TestPassword123!"))
        self.assertEqual(response.status_code, 302)

    def test_email_must_be_unique(self):
        User.objects.create_user(
            username="user1",
            email="test@example.com",
            password="TestPassword123!",
        )
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "user2",
                "email": "test@example.com",
                "password1": "TestPassword123!",
                "password2": "TestPassword123!",
            },
        )
        self.assertEqual(User.objects.count(), 1)
        self.assertContains(response, "Ya existe un usuario con este email.")


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
        )

    def test_user_can_login(self):
        logged_in = self.client.login(
            username="laura",
            password="TestPassword123!",
        )
        self.assertTrue(logged_in)


class ProfileTests(TestCase):
    def test_profile_requires_login(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 302)

    def test_logged_user_can_view_profile(self):
        user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
        )
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "laura")
