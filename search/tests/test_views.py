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
        )
        self.category = Category.objects.create(
            name="Idiomas",
            slug="idiomas",
        )
        self.course = Course.objects.create(
            academy=self.academy,
            category=self.category,
            title="Inglés B2",
            slug="ingles-b2",
            description="Curso de inglés",
            status="published",
        )
        self.teacher = Teacher.objects.create(
            academy=self.academy,
            first_name="Laura",
            last_name="García",
            specialty="Inglés",
        )

    def test_global_search_is_public(self):
        response = self.client.get(reverse("search:global"))
        self.assertEqual(response.status_code, 200)

    def test_global_search_without_query(self):
        response = self.client.get(reverse("search:global"))
        self.assertEqual(response.status_code, 200)

    def test_global_search_no_results(self):
        response = self.client.get(
            reverse("search:global"),
            {"q": "xyz123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["results"]), 0)

    def test_global_search_finds_course(self):
        response = self.client.get(
            reverse("search:global"),
            {"q": "Inglés"},
        )
        results = response.context["results"]
        course_results = [r for r in results if isinstance(r, Course)]
        self.assertGreaterEqual(len(course_results), 1)
        self.assertEqual(course_results[0].pk, self.course.pk)

    def test_global_search_finds_academy(self):
        response = self.client.get(
            reverse("search:global"),
            {"q": "English"},
        )
        results = response.context["results"]
        academy_results = [r for r in results if isinstance(r, Academy)]
        self.assertGreaterEqual(len(academy_results), 1)
        self.assertEqual(academy_results[0].pk, self.academy.pk)

    def test_global_search_finds_teacher(self):
        response = self.client.get(
            reverse("search:global"),
            {"q": "Laura"},
        )
        results = response.context["results"]
        teacher_results = [r for r in results if isinstance(r, Teacher)]
        self.assertGreaterEqual(len(teacher_results), 1)
        self.assertEqual(teacher_results[0].pk, self.teacher.pk)