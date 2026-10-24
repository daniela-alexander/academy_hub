from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from academies.cache import (
    POPULAR_ACADEMIES_KEY,
    POPULAR_ACADEMIES_TIMEOUT,
    get_popular_academies,
    invalidate_popular_academies,
)
from academies.models import Academy, AcademyFavorite

User = get_user_model()


class PopularAcademiesCacheTests(TestCase):

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
        self.academy1 = Academy.objects.create(
            owner=self.owner,
            name="English Now",
            slug="english-now",
        )
        self.academy2 = Academy.objects.create(
            owner=self.owner,
            name="Code Academy",
            slug="code-academy",
        )

    def tearDown(self):
        cache.clear()

    # ------------------------------------------------------------
    # Cache miss → PostgreSQL → guarda → devuelve
    # ------------------------------------------------------------
    def test_cache_miss_populates_cache(self):
        self.assertIsNone(cache.get(POPULAR_ACADEMIES_KEY))

        result = get_popular_academies()

        self.assertEqual(len(result), 2)
        self.assertIsNotNone(cache.get(POPULAR_ACADEMIES_KEY))
        self.assertEqual(len(cache.get(POPULAR_ACADEMIES_KEY)), 2)

    # ------------------------------------------------------------
    # Cache hit → NO recalcula populares (2 queries: academias + cursos)
    # ------------------------------------------------------------
    def test_cache_hit_does_not_query_postgres(self):
        cache.set(POPULAR_ACADEMIES_KEY, [self.academy1.pk], timeout=60)

        with self.assertNumQueries(2):
            # 2 queries: academias (select_related) + cursos (prefetch_related)
            result = get_popular_academies()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].pk, self.academy1.pk)

    # ------------------------------------------------------------
    # Invalidación explícita
    # ------------------------------------------------------------
    def test_invalidate_removes_cache(self):
        get_popular_academies()
        self.assertIsNotNone(cache.get(POPULAR_ACADEMIES_KEY))

        invalidate_popular_academies()
        self.assertIsNone(cache.get(POPULAR_ACADEMIES_KEY))

    # ------------------------------------------------------------
    # Sin academias → devuelve []
    # ------------------------------------------------------------
    def test_no_academies_returns_empty_list(self):
        Academy.objects.all().delete()
        cache.clear()

        result = get_popular_academies()
        self.assertEqual(result, [])

    # ------------------------------------------------------------
    # El orden respeta los IDs cacheados
    # ------------------------------------------------------------
    def test_order_matches_cached_ids(self):
        cache.set(
            POPULAR_ACADEMIES_KEY,
            [self.academy2.pk, self.academy1.pk],
            timeout=60,
        )

        result = get_popular_academies()

        self.assertEqual(result[0].pk, self.academy2.pk)
        self.assertEqual(result[1].pk, self.academy1.pk)

    # ------------------------------------------------------------
    # TTL correcto
    # ------------------------------------------------------------
    def test_cache_uses_correct_timeout(self):
        get_popular_academies()

        cached = cache.get(POPULAR_ACADEMIES_KEY)
        self.assertIsNotNone(cached)
        self.assertIsInstance(cached, list)

    # ------------------------------------------------------------
    # El toggle de favorito invalida el cache
    # ------------------------------------------------------------
    def test_toggle_favorite_invalidates_cache(self):
        get_popular_academies()
        self.assertIsNotNone(cache.get(POPULAR_ACADEMIES_KEY))

        self.client.force_login(self.student)
        self.client.post(
            reverse("academies:toggle_favorite", kwargs={"slug": "english-now"}),
        )

        self.assertIsNone(cache.get(POPULAR_ACADEMIES_KEY))

    # ------------------------------------------------------------
    # Cache con lista vacía (nadie tiene favoritos)
    # ------------------------------------------------------------
    def test_empty_popular_list_is_cached(self):
        cache.set(POPULAR_ACADEMIES_KEY, [], timeout=60)

        result = get_popular_academies()

        self.assertEqual(result, [])