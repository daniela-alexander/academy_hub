from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from academies.models import Academy

User = get_user_model()


class AcademyAPITests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="TestPassword123!",
            is_academy=True,
        )
        self.academy = Academy.objects.create(
            owner=self.owner,
            name="English Now",
            slug="english-now",
            city="Madrid",
        )

    def test_list_is_public(self):
        response = self.client.get("/api/v1/academies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_by_slug(self):
        response = self.client.get("/api/v1/academies/english-now/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "English Now")

    def test_mine_requires_auth(self):
        response = self.client.get("/api/v1/academies/mine/")
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_mine_returns_own_academies(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get("/api/v1/academies/mine/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_by_city(self):
        response = self.client.get("/api/v1/academies/?city=Madrid")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
