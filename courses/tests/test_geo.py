from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse

from academies.models import Academy
from core.geo_services import get_courses_nearby
from courses.models import Category, Course, CourseStatus

User = get_user_model()

BARCELONA = {"lat": "41.3870", "lng": "2.1700"}


class CourseGeoTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="testpass123",
            is_academy=True,
        )
        self.category = Category.objects.create(name="Idiomas", slug="idiomas")
        # Academia en L'Hospitalet
        self.academy_near = Academy.objects.create(
            owner=self.owner,
            name="English Now Barcelona",
            slug="english-now-barcelona",
            location=Point(2.0997, 41.3598, srid=4326),
            location_name="L'Hospitalet",
        )
        # Academia en Madrid
        self.academy_far = Academy.objects.create(
            owner=self.owner,
            name="English Now Madrid",
            slug="english-now-madrid",
            location=Point(-3.7038, 40.4168, srid=4326),
            location_name="Madrid",
        )
        self.course_near = Course.objects.create(
            academy=self.academy_near,
            category=self.category,
            title="Inglés B2 Barcelona",
            slug="ingles-b2-barcelona",
            description="...",
            status=CourseStatus.PUBLISHED,
        )
        self.course_far = Course.objects.create(
            academy=self.academy_far,
            category=self.category,
            title="Inglés B2 Madrid",
            slug="ingles-b2-madrid",
            description="...",
            status=CourseStatus.PUBLISHED,
        )


class CourseSpatialQueryTests(CourseGeoTestCase):
    def test_filter_nearby_courses_within_10km(self):
        results = list(
            get_courses_nearby(latitude=41.3870, longitude=2.1700, radius_km=10)
        )
        self.assertIn(self.course_near, results)
        self.assertNotIn(self.course_far, results)
        self.assertTrue(results[0].distance.km < 10)

    def test_ordering_by_distance(self):
        results = list(
            get_courses_nearby(latitude=41.3870, longitude=2.1700, radius_km=600)
        )
        self.assertEqual(results, [self.course_near, self.course_far])

    def test_unpublished_courses_are_excluded(self):
        self.course_near.status = CourseStatus.DRAFT
        self.course_near.save()
        results = list(
            get_courses_nearby(latitude=41.3870, longitude=2.1700, radius_km=10)
        )
        self.assertNotIn(self.course_near, results)

    def test_courses_from_academies_without_location_are_excluded(self):
        academy_no_location = Academy.objects.create(
            owner=self.owner,
            name="Sin ubicación",
            slug="sin-ubicacion",
        )
        course_no_location = Course.objects.create(
            academy=academy_no_location,
            category=self.category,
            title="Curso sin ubicación",
            slug="curso-sin-ubicacion",
            description="...",
            status=CourseStatus.PUBLISHED,
        )
        results = list(
            get_courses_nearby(latitude=41.3870, longitude=2.1700, radius_km=10)
        )
        self.assertNotIn(course_no_location, results)


class CourseListGeoViewTests(CourseGeoTestCase):
    def _get(self, **params):
        return self.client.get(reverse("courses:list"), params)

    def test_filters_by_distance(self):
        response = self._get(**BARCELONA, distance_km="10")
        self.assertEqual(list(response.context["courses"]), [self.course_near])

    def test_distance_order_takes_precedence_over_ordering(self):
        response = self._get(**BARCELONA, distance_km="600", ordering="oldest")
        self.assertEqual(
            list(response.context["courses"]),
            [self.course_near, self.course_far],
        )

    def test_invalid_coordinates_are_ignored(self):
        response = self._get(lat="abc", lng="2.17")
        self.assertEqual(len(response.context["courses"]), 2)

    def test_form_has_geo_fields(self):
        response = self._get()
        for field in ("lat", "lng", "distance_km"):
            self.assertContains(response, f'name="{field}"')
