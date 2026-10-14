from datetime import date
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.test_base import VerboseTestCase

from academies.models import Academy

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

class RegisterTests(VerboseTestCase):

    def test_register_page_returns_200(self):

        response = self.client.get(
            reverse("accounts:register")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_user_can_register(self):

        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "laura",
                "email": "laura@example.com",
                "first_name": "Laura",
                "last_name": "Garcia",
                "is_student": True,
                "password1": "TestPassword123!",
                "password2": "TestPassword123!",
            },
        )

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username="laura")

        self.assertEqual(user.email, "laura@example.com")
        self.assertTrue(user.is_student)
        self.assertTrue(
            user.check_password("TestPassword123!")
        )

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

        self.assertEqual(
            User.objects.count(),
            1,
        )

        self.assertContains(
            response,
            "Ya existe un usuario con este email.",
        )
    
class LoginTests(VerboseTestCase):

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

class ProfileTests(VerboseTestCase):

    def test_profile_requires_login(self):

        response = self.client.get(
            reverse("accounts:profile")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_logged_user_can_view_profile(self):

        user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse("accounts:profile")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "laura",
        )

class AcademyViewTests(VerboseTestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="TestPassword123!",
            is_academy=True,
        )
        self.other = User.objects.create_user(
            username="codeacademy",
            email="info@codeacademy.com",
            password="TestPassword123!",
            is_academy=True,
        )
        self.academy = Academy.objects.create(
            owner=self.owner,
            name="English Now",
            slug="english-now",
        )

    def test_academy_list_is_public(self):
        response = self.client.get(reverse("academies:list"))
        self.assertEqual(response.status_code, 200)

    def test_academy_detail_is_public(self):
        response = self.client.get(
            reverse("academies:detail", kwargs={"slug": "english-now"})
        )
        self.assertEqual(response.status_code, 200)

    def test_create_requires_login(self):
        response = self.client.get(reverse("academies:create"))
        self.assertEqual(response.status_code, 302)

    def test_other_user_cannot_edit(self):
        self.client.force_login(self.other)
        response = self.client.get(
            reverse("academies:update", kwargs={"slug": "english-now"})
        )
        self.assertEqual(response.status_code, 403)

    def test_owner_can_edit(self):
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse("academies:update", kwargs={"slug": "english-now"})
        )
        self.assertEqual(response.status_code, 200)
