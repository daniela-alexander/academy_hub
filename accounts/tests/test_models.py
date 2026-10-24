from django.contrib.auth import get_user_model
from core.test_base import VerboseTestCase

User = get_user_model()

class UserModelTests(VerboseTestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
        )

        self.assertEqual(user.username, "laura")
        self.assertEqual(user.email, "laura@example.com")
        self.assertTrue(user.check_password("TestPassword123!"))
        self.assertFalse(user.is_academy)
        self.assertFalse(user.is_student)
        self.assertFalse(user.is_verified)

    def test_email_must_be_unique(self):
        User.objects.create_user(
            username="user1",
            email="test@example.com",
            password="TestPassword123!",
        )

        with self.assertRaises(Exception):
            User.objects.create_user(
                username="user2",
                email="test@example.com",
                password="TestPassword123!",
            )

    def test_user_can_be_academy(self):
        user = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="TestPassword123!",
            is_academy=True,
        )

        self.assertTrue(user.is_academy)
        self.assertFalse(user.is_student)

    def test_user_can_be_student(self):
        user = User.objects.create_user(
            username="carlos",
            email="carlos@example.com",
            password="TestPassword123!",
            is_student=True,
        )

        self.assertTrue(user.is_student)
        self.assertFalse(user.is_academy)

    def test_user_can_have_city(self):
        user = User.objects.create_user(
            username="ana",
            email="ana@example.com",
            password="TestPassword123!",
            city="Barcelona",
        )

        self.assertEqual(user.city, "Barcelona")

    def test_user_can_have_birth_date(self):
        from datetime import date

        user = User.objects.create_user(
            username="pedro",
            email="pedro@example.com",
            password="TestPassword123!",
            birth_date=date(1990, 5, 15),
        )

        self.assertEqual(user.birth_date, date(1990, 5, 15))

    def test_user_string_representation(self):
        user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
        )

        self.assertEqual(str(user), "laura")


    def test_user_can_have_phone(self):
        user = User.objects.create_user(
            username="ana",
            email="ana@example.com",
            password="secure_password_123",
            phone="600123456",
        )

        self.assertEqual(user.phone, "600123456")
