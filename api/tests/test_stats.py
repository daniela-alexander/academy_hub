from rest_framework import status
from rest_framework.test import APITestCase


class StatsAPITests(APITestCase):

    def test_stats_is_public(self):
        response = self.client.get("/api/v1/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("courses", response.data)
        self.assertIn("academies", response.data)
