from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from academies.cache import POPULAR_ACADEMIES_KEY
from academies.models import Academy, AcademyFavorite

User = get_user_model()


class AcademyViewTests(TestCase):

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


class AcademySearchTests(TestCase):

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
        Academy.objects.create(
            owner=self.owner,
            name="Code Academy",
            slug="code-academy",
            city="Barcelona",
        )

    def test_search_by_name(self):
        response = self.client.get(
            reverse("academies:list"),
            {"q": "English"},
        )
        self.assertContains(response, "English Now")
        self.assertNotContains(response, "Code Academy")

    def test_filter_by_city(self):
        response = self.client.get(
            reverse("academies:list"),
            {"city": "Barcelona"},
        )
        self.assertContains(response, "Code Academy")
        self.assertNotContains(response, "English Now")


class AcademyFavoriteTests(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="TestPassword123!",
            is_academy=True,
        )
        self.student = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.academy = Academy.objects.create(
            owner=self.owner,
            name="English Now",
            slug="english-now",
        )

    def test_student_can_add_favorite(self):
        self.client.force_login(self.student)
        self.client.post(
            reverse("academies:toggle_favorite", kwargs={"slug": "english-now"}),
        )
        self.assertTrue(
            AcademyFavorite.objects.filter(
                user=self.student,
                academy=self.academy,
            ).exists()
        )

    def test_owner_cannot_favorite_own_academy(self):
        self.client.force_login(self.owner)
        self.client.post(
            reverse("academies:toggle_favorite", kwargs={"slug": "english-now"}),
        )
        self.assertFalse(
            AcademyFavorite.objects.filter(
                user=self.owner,
                academy=self.academy,
            ).exists()
        )


class AcademyFavoriteCacheInvalidationTests(TestCase):

    def setUp(self):
        cache.clear()
        self.owner = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="TestPassword123!",
            is_academy=True,
        )
        self.student = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.academy = Academy.objects.create(
            owner=self.owner,
            name="English Now",
            slug="english-now",
        )

    def tearDown(self):
        cache.clear()

    def test_toggle_favorite_invalidates_popular_cache(self):
        cache.set(POPULAR_ACADEMIES_KEY, [99, 100], timeout=60)

        self.client.force_login(self.student)
        self.client.post(
            reverse("academies:toggle_favorite", kwargs={"slug": "english-now"}),
        )

        self.assertIsNone(cache.get(POPULAR_ACADEMIES_KEY))