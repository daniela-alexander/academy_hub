from django.contrib.auth import get_user_model
from django.test import TestCase

from academies.models import Academy
from academies.services import verify_academy

User = get_user_model()


class VerifyAcademyTests(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="TestPassword123!",
            is_academy=True,
        )
        self.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="TestPassword123!",
            is_staff=True,
        )
        self.academy = Academy.objects.create(
            owner=self.owner,
            name="English Now",
            slug="english-now",
        )

    def test_staff_can_verify_academy(self):
        verify_academy(self.academy.pk, self.staff)
        self.academy.refresh_from_db()
        self.assertTrue(self.academy.is_verified)

    def test_non_staff_cannot_verify_academy(self):
        with self.assertRaises(ValueError):
            verify_academy(self.academy.pk, self.owner)