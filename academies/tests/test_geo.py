from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse

from academies.models import Academy
from core.geo_services import get_academies_nearby

User = get_user_model()

BARCELONA = {"lat": "41.3870", "lng": "2.1700"}


class AcademyGeoTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="testpass123",
            is_academy=True,
        )
        # Academia 1: L'Hospitalet de Llobregat (41.3598, 2.0997)
        self.academy_near = Academy.objects.create(
            owner=self.owner,
            name="English Now Barcelona",
            slug="english-now-barcelona",
            location=Point(2.0997, 41.3598, srid=4326),
            location_name="L'Hospitalet",
        )
        # Academia 2: Madrid Centro (40.4168, -3.7038)
        self.academy_far = Academy.objects.create(
            owner=self.owner,
            name="English Now Madrid",
            slug="english-now-madrid",
            location=Point(-3.7038, 40.4168, srid=4326),
            location_name="Madrid",
        )


class AcademySpatialQueryTests(AcademyGeoTestCase):
    def test_filter_nearby_academies_within_10km(self):
        # L'Hospitalet está a ~6-7 km de Plaça de Catalunya; Madrid, a ~500 km.
        results = list(
            get_academies_nearby(latitude=41.3870, longitude=2.1700, radius_km=10)
        )
        self.assertIn(self.academy_near, results)
        self.assertNotIn(self.academy_far, results)
        self.assertTrue(results[0].distance.km < 10)

    def test_academies_outside_radius_are_excluded(self):
        results = list(
            get_academies_nearby(latitude=41.3870, longitude=2.1700, radius_km=2)
        )
        self.assertNotIn(self.academy_near, results)
        self.assertNotIn(self.academy_far, results)

    def test_ordering_by_distance(self):
        results = list(
            get_academies_nearby(latitude=41.3870, longitude=2.1700, radius_km=600)
        )
        self.assertEqual(results, [self.academy_near, self.academy_far])

    def test_inactive_academies_are_excluded(self):
        self.academy_near.is_active = False
        self.academy_near.save()
        results = list(
            get_academies_nearby(latitude=41.3870, longitude=2.1700, radius_km=10)
        )
        self.assertNotIn(self.academy_near, results)

    def test_academies_without_location_are_excluded(self):
        academy_no_location = Academy.objects.create(
            owner=self.owner,
            name="Sin ubicación",
            slug="sin-ubicacion",
        )
        results = list(
            get_academies_nearby(latitude=41.3870, longitude=2.1700, radius_km=10)
        )
        self.assertNotIn(academy_no_location, results)


class AcademyListGeoViewTests(AcademyGeoTestCase):
    def _get(self, **params):
        return self.client.get(reverse("academies:list"), params)

    def test_filters_by_distance(self):
        response = self._get(**BARCELONA, distance_km="10")
        self.assertEqual(
            list(response.context["academies"]), [self.academy_near]
        )

    def test_distance_order_takes_precedence_over_ordering(self):
        response = self._get(**BARCELONA, distance_km="600", ordering="name_desc")
        self.assertEqual(
            list(response.context["academies"]),
            [self.academy_near, self.academy_far],
        )

    def test_default_radius_is_20_km(self):
        response = self._get(**BARCELONA)
        self.assertEqual(
            list(response.context["academies"]), [self.academy_near]
        )

    def test_invalid_coordinates_are_ignored(self):
        response = self._get(lat="abc", lng="2.17")
        self.assertEqual(len(response.context["academies"]), 2)

    def test_form_has_geo_fields(self):
        response = self._get()
        for field in ("lat", "lng", "distance_km"):
            self.assertContains(response, f'name="{field}"')
