from core.test_base import VerboseTestCase
from django.urls import reverse

from accounts.models import User
from academies.models import Academy, Teacher
from courses.models import Category, Course, CourseStatus


class SearchTests(VerboseTestCase):
    def test_search_page_is_public(self):
        response = self.client.get(reverse("search:course_search"))
        self.assertEqual(response.status_code, 200)


class GlobalSearchTests(VerboseTestCase):
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
            description="Academia de idiomas",
        )
        self.category = Category.objects.create(name="Idiomas", slug="idiomas")
        self.course = Course.objects.create(
            academy=self.academy,
            category=self.category,
            title="Inglés B2 intensivo",
            slug="ingles-b2",
            description="Curso intensivo",
            status=CourseStatus.PUBLISHED,
        )
        self.teacher = Teacher.objects.create(
            academy=self.academy,
            first_name="Laura",
            last_name="Gómez",
            specialty="Inglés",
        )

    def test_global_search_is_public(self):
        response = self.client.get(reverse("search:global"))
        self.assertEqual(response.status_code, 200)

    def test_global_search_without_query(self):
        response = self.client.get(reverse("search:global"))
        self.assertEqual(response.context["results"], [])

    def test_global_search_finds_course(self):
        response = self.client.get(reverse("search:global"), {"q": "B2"})
        types = [item["type"] for item in response.context["results"]]
        self.assertIn("course", types)

    def test_global_search_finds_academy(self):
        response = self.client.get(reverse("search:global"), {"q": "English"})
        types = [item["type"] for item in response.context["results"]]
        self.assertIn("academy", types)

    def test_global_search_finds_teacher(self):
        response = self.client.get(reverse("search:global"), {"q": "Gómez"})
        types = [item["type"] for item in response.context["results"]]
        self.assertIn("teacher", types)

    def test_global_search_no_results(self):
        response = self.client.get(reverse("search:global"), {"q": "zzzzz"})
        self.assertEqual(response.context["results"], [])
