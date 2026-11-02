from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from rest_framework import status
from rest_framework.test import APITestCase

from academies.models import Academy
from courses.models import Category, Course, CourseStatus

User = get_user_model()

BARCELONA = {"lat": "41.3870", "lng": "2.1700"}
INVALID_PARAMS = [
    {"lat": "abc", "lng": "2.17"},
    {"lat": "41.38", "lng": "abc"},
    {"lat": "nan", "lng": "2.17"},
    {"lat": "inf", "lng": "2.17"},
    {"lat": "999", "lng": "2.17"},
    {"lat": "41.38", "lng": "999"},
    {**BARCELONA, "distance_km": "abc"},
    {**BARCELONA, "distance_km": "-5"},
    {**BARCELONA, "distance_km": "nan"},
    {**BARCELONA, "distance_km": "inf"},
]


class GeoAPITestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="testpass123",
            is_academy=True,
        )
        self.category = Category.objects.create(name="Idiomas", slug="idiomas")
        self.academy_near = Academy.objects.create(
            owner=self.owner,
            name="English Now Barcelona",
            slug="english-now-barcelona",
            location=Point(2.0997, 41.3598, srid=4326),
            location_name="L'Hospitalet",
        )
        self.academy_far = Academy.objects.create(
            owner=self.owner,
            name="English Now Madrid",
            slug="english-now-madrid",
            location=Point(-3.7038, 40.4168, srid=4326),
            location_name="Madrid",
        )
        self.academy_no_location = Academy.objects.create(
            owner=self.owner,
            name="Sin ubicación",
            slug="sin-ubicacion",
        )
        self.course_near = self._create_course(self.academy_near, "barcelona")
        self.course_far = self._create_course(self.academy_far, "madrid")
        self.course_no_location = self._create_course(
            self.academy_no_location, "sin-ubicacion"
        )

    def _create_course(self, academy, slug):
        return Course.objects.create(
            academy=academy,
            category=self.category,
            title=f"Curso {slug}",
            slug=slug,
            description="...",
            status=CourseStatus.PUBLISHED,
        )


class AcademyGeoAPITests(GeoAPITestCase):
    URL = "/api/v1/academies/"

    def _slugs(self, params):
        response = self.client.get(self.URL, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return [academy["slug"] for academy in response.data["results"]]

    def test_exposes_coordinates_without_raw_location(self):
        response = self.client.get(f"{self.URL}{self.academy_near.slug}/")
        self.assertEqual(response.data["latitude"], 41.3598)
        self.assertEqual(response.data["longitude"], 2.0997)
        self.assertEqual(response.data["location_name"], "L'Hospitalet")
        self.assertIsNone(response.data["distance_km"])
        self.assertNotIn("location", response.data)

    def test_academy_without_location_has_null_coordinates(self):
        response = self.client.get(f"{self.URL}{self.academy_no_location.slug}/")
        self.assertIsNone(response.data["latitude"])
        self.assertIsNone(response.data["longitude"])

    def test_filters_by_distance(self):
        slugs = self._slugs({**BARCELONA, "distance_km": "10"})
        self.assertEqual(slugs, [self.academy_near.slug])

    def test_default_radius_is_20_km(self):
        self.assertEqual(self._slugs(BARCELONA), [self.academy_near.slug])

    def test_reports_distance_in_km(self):
        response = self.client.get(self.URL, {**BARCELONA, "distance_km": "10"})
        distance_km = response.data["results"][0]["distance_km"]
        self.assertGreater(distance_km, 5)
        self.assertLess(distance_km, 10)

    def test_orders_by_distance(self):
        Academy.objects.filter(pk=self.academy_far.pk).update(
            created_at=self.academy_near.created_at.replace(year=2030)
        )
        slugs = self._slugs({**BARCELONA, "distance_km": "600"})
        self.assertEqual(slugs, [self.academy_near.slug, self.academy_far.slug])

    def test_invalid_params_return_unfiltered_list(self):
        for params in INVALID_PARAMS:
            with self.subTest(params=params):
                self.assertEqual(len(self._slugs(params)), 3)

    def test_without_params_keeps_all_academies(self):
        self.assertEqual(len(self._slugs({})), 3)


class CourseGeoAPITests(GeoAPITestCase):
    URL = "/api/v1/courses/"

    def _slugs(self, params):
        response = self.client.get(self.URL, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return [course["slug"] for course in response.data["results"]]

    def test_exposes_academy_coordinates(self):
        response = self.client.get(f"{self.URL}{self.course_near.pk}/")
        self.assertEqual(response.data["latitude"], 41.3598)
        self.assertEqual(response.data["longitude"], 2.0997)
        self.assertIsNone(response.data["distance_km"])

    def test_course_without_location_has_null_coordinates(self):
        response = self.client.get(f"{self.URL}{self.course_no_location.pk}/")
        self.assertIsNone(response.data["latitude"])
        self.assertIsNone(response.data["longitude"])

    def test_filters_by_distance(self):
        slugs = self._slugs({**BARCELONA, "distance_km": "10"})
        self.assertEqual(slugs, [self.course_near.slug])

    def test_reports_distance_in_km(self):
        response = self.client.get(self.URL, {**BARCELONA, "distance_km": "10"})
        distance_km = response.data["results"][0]["distance_km"]
        self.assertGreater(distance_km, 5)
        self.assertLess(distance_km, 10)

    def test_orders_by_distance(self):
        Course.objects.filter(pk=self.course_far.pk).update(
            created_at=self.course_near.created_at.replace(year=2030)
        )
        slugs = self._slugs({**BARCELONA, "distance_km": "600"})
        self.assertEqual(slugs, [self.course_near.slug, self.course_far.slug])

    def test_invalid_params_return_unfiltered_list(self):
        for params in INVALID_PARAMS:
            with self.subTest(params=params):
                self.assertEqual(len(self._slugs(params)), 3)
