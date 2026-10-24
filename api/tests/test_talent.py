from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from talent.models import TalentPassport

User = get_user_model()


class TalentAPITests(APITestCase):

    def setUp(self):
        self.student = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )

    def test_passport_mine_creates_on_demand(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/v1/passport/mine/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            TalentPassport.objects.filter(student=self.student).exists()
        )
