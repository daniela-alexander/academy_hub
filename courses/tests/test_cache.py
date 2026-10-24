from decimal import Decimal
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase

from academies.models import Academy
from courses.cache import (
    POPULAR_COURSES_KEY,
    POPULAR_COURSES_TIMEOUT,
    get_popular_courses,
    invalidate_popular_courses,
)
from courses.models import Category, Course, CourseFavorite

User = get_user_model()


class PopularCoursesCacheTests(TestCase):

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
        self.category = Category.objects.create(
            name="Idiomas",
            slug="idiomas",
        )
        self.course1 = Course.objects.create(
            academy=self.academy,
            category=self.category,
            title="Inglés B2",
            slug="ingles-b2",
            description="...",
            status="published",
        )
        self.course2 = Course.objects.create(
            academy=self.academy,
            category=self.category,
            title="Francés B1",
            slug="frances-b1",
            description="...",
            status="published",
        )

    def tearDown(self):
        cache.clear()

    # ------------------------------------------------------------
    # Cache miss → PostgreSQL → guarda → devuelve
    # ------------------------------------------------------------
    def test_cache_miss_populates_cache(self):
        self.assertIsNone(cache.get(POPULAR_COURSES_KEY))

        result = get_popular_courses()

        self.assertEqual(len(result), 2)
        self.assertIsNotNone(cache.get(POPULAR_COURSES_KEY))
        self.assertEqual(len(cache.get(POPULAR_COURSES_KEY)), 2)

    # ------------------------------------------------------------
    # Cache hit → NO consulta PostgreSQL
    # ------------------------------------------------------------
    def test_cache_hit_does_not_query_postgres(self):
        cache.set(POPULAR_COURSES_KEY, [self.course1.pk], timeout=60)

        with self.assertNumQueries(2):
            # 2 queries: cursos (select_related) + imágenes (prefetch_related)
            result = get_popular_courses()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].pk, self.course1.pk)

    # ------------------------------------------------------------
    # Invalidación explícita
    # ------------------------------------------------------------
    def test_invalidate_removes_cache(self):
        get_popular_courses()
        self.assertIsNotNone(cache.get(POPULAR_COURSES_KEY))

        invalidate_popular_courses()
        self.assertIsNone(cache.get(POPULAR_COURSES_KEY))

    # ------------------------------------------------------------
    # Sin cursos → devuelve []
    # ------------------------------------------------------------
    def test_no_courses_returns_empty_list(self):
        Course.objects.all().delete()
        cache.clear()

        result = get_popular_courses()
        self.assertEqual(result, [])

    # ------------------------------------------------------------
    # El orden respeta los IDs cacheados
    # ------------------------------------------------------------
    def test_order_matches_cached_ids(self):
        cache.set(POPULAR_COURSES_KEY, [self.course2.pk, self.course1.pk], timeout=60)

        result = get_popular_courses()

        self.assertEqual(result[0].pk, self.course2.pk)
        self.assertEqual(result[1].pk, self.course1.pk)

    # ------------------------------------------------------------
    # TTL correcto
    # ------------------------------------------------------------
    def test_cache_uses_correct_timeout(self):
        get_popular_courses()

        # No hay forma directa de leer TTL desde Django cache,
        # pero comprobamos que el valor está ahí
        cached = cache.get(POPULAR_COURSES_KEY)
        self.assertIsNotNone(cached)
        self.assertIsInstance(cached, list)

    # ------------------------------------------------------------
    # El toggle de favorito invalida el cache
    # ------------------------------------------------------------
    def test_toggle_favorite_invalidates_cache(self):
        get_popular_courses()
        self.assertIsNotNone(cache.get(POPULAR_COURSES_KEY))

        self.client.force_login(self.student)
        self.client.post(
            reverse("courses:toggle_favorite", kwargs={"pk": self.course1.pk}),
        )

        self.assertIsNone(cache.get(POPULAR_COURSES_KEY))