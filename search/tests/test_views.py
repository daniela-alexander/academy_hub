from core.test_base import VerboseTestCase
from django.urls import reverse


class SearchTests(VerboseTestCase):
    def test_search_page_is_public(self):
        response = self.client.get(reverse("search:course_search"))
        self.assertEqual(response.status_code, 200)
