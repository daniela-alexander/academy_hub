from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="secure_password_123",
            is_student="True",
        )

        self.assertEqual(user.username, "laura")
        self.assertTrue(user.check_password("secure_password_123"))
        self.assertFalse(user.is_academy)
        self.assertTrue(user.is_student)

    def test_user_can_have_city(self):
        user = User.objects.create_user(
            username="carlos",
            email="carlos@example.com",
            password="secure_password_123",
            city="Barcelona",
        )

        self.assertEqual(user.city, "Barcelona")

    def test_user_can_have_phone(self):
        user = User.objects.create_user(
            username="ana",
            email="ana@example.com",
            password="secure_password_123",
            phone="600123456",
        )

        self.assertEqual(user.phone, "600123456")