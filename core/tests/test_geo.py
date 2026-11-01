from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point

from academies.models import Academy
from core.geo_services import get_academies_nearby, get_courses_nearby
from core.test_base import VerboseTestCase
from courses.models import Category, Course, CourseStatus

User = get_user_model()

# Punto de búsqueda: Plaça de Catalunya, Barcelona.
ORIGIN_LAT = 41.3870
ORIGIN_LNG = 2.1700


def make_academy(name, longitude=None, latitude=None, **extra):
    """Crea una academia con su propio dueño. Point recibe primero la longitud."""
    slug = name.lower().replace(" ", "-")
    owner = User.objects.create_user(
        username=slug,
        email=f"{slug}@example.com",
        password="pwd",
        is_academy=True,
    )
    location = None
    if longitude is not None:
        location = Point(longitude, latitude, srid=4326)
    return Academy.objects.create(
        owner=owner,
        name=name,
        slug=slug,
        location=location,
        **extra,
    )


class GeoFixtureMixin:

    def setUp(self):
        # Gràcia: a unos 2 km del origen.
        self.academy_closest = make_academy("Gracia", 2.1565, 41.4036)
        # L'Hospitalet de Llobregat: a unos 6,6 km del origen.
        self.academy_near = make_academy("Hospitalet", 2.0997, 41.3598)
        # Madrid centro: a unos 500 km del origen.
        self.academy_far = make_academy("Madrid", -3.7038, 40.4168)


class AcademiesNearbyTests(GeoFixtureMixin, VerboseTestCase):

    def nearby(self, radius_km=10):
        return list(
            get_academies_nearby(
                latitude=ORIGIN_LAT,
                longitude=ORIGIN_LNG,
                radius_km=radius_km,
            )
        )

    def test_includes_academy_within_radius(self):
        self.assertIn(self.academy_near, self.nearby())

    def test_excludes_academy_outside_radius(self):
        self.assertNotIn(self.academy_far, self.nearby())

    def test_radius_limits_results(self):
        results = self.nearby(radius_km=5)

        self.assertIn(self.academy_closest, results)
        self.assertNotIn(self.academy_near, results)

    def test_results_are_ordered_by_distance(self):
        self.assertEqual(
            self.nearby(),
            [self.academy_closest, self.academy_near],
        )

    def test_distance_is_calculated_in_km(self):
        result = next(
            academy
            for academy in self.nearby()
            if academy == self.academy_near
        )

        self.assertAlmostEqual(result.distance.km, 6.6, delta=0.5)

    def test_excludes_inactive_academy(self):
        inactive = make_academy("Inactiva", 2.1700, 41.3870, is_active=False)

        self.assertNotIn(inactive, self.nearby())

    def test_excludes_academy_without_location(self):
        without_location = make_academy("Sin ubicacion")

        self.assertNotIn(without_location, self.nearby())


class CoursesNearbyTests(GeoFixtureMixin, VerboseTestCase):

    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(
            name="Idiomas",
            slug="idiomas",
        )

    def make_course(self, academy, title, status=CourseStatus.PUBLISHED):
        return Course.objects.create(
            academy=academy,
            category=self.category,
            title=title,
            slug=title.lower().replace(" ", "-"),
            description="...",
            status=status,
        )

    def nearby(self, radius_km=10):
        return list(
            get_courses_nearby(
                latitude=ORIGIN_LAT,
                longitude=ORIGIN_LNG,
                radius_km=radius_km,
            )
        )

    def test_includes_published_course_within_radius(self):
        course = self.make_course(self.academy_near, "Ingles B2")

        self.assertIn(course, self.nearby())

    def test_excludes_course_from_distant_academy(self):
        course = self.make_course(self.academy_far, "Python Inicial")

        self.assertNotIn(course, self.nearby())

    def test_excludes_unpublished_courses(self):
        draft = self.make_course(
            self.academy_near,
            "Borrador",
            status=CourseStatus.DRAFT,
        )
        archived = self.make_course(
            self.academy_near,
            "Archivado",
            status=CourseStatus.ARCHIVED,
        )

        results = self.nearby()

        self.assertNotIn(draft, results)
        self.assertNotIn(archived, results)

    def test_excludes_course_from_academy_without_location(self):
        academy = make_academy("Sin ubicacion")
        course = self.make_course(academy, "Sin sede")

        self.assertNotIn(course, self.nearby())

    def test_courses_are_ordered_by_academy_distance(self):
        far_course = self.make_course(self.academy_near, "Curso lejano")
        close_course = self.make_course(self.academy_closest, "Curso cercano")

        self.assertEqual(self.nearby(), [close_course, far_course])
