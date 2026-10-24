from django.contrib.auth import get_user_model
from django.urls import reverse

from academies.models import Academy
from core.test_base import VerboseTestCase

from decimal import Decimal

from academies.models import Academy
from courses.models import (
    Category,
    Course,
    CourseLevel,
    CourseModality,
    CourseStatus,
    EnrollmentMode,
    Convocatoria,
    CourseFavorite,
)

User = get_user_model()

class TextChoicesTest(VerboseTestCase):

    def test_course_level_valores(self):
        self.assertEqual(CourseLevel.BEGINNER, "beginner")
        self.assertEqual(CourseLevel.INTERMEDIATE, "intermediate")
        self.assertEqual(CourseLevel.ADVANCED, "advanced")
        self.assertEqual(CourseLevel.EXPERT, "expert")

    def test_course_level_labels(self):
        self.assertEqual(CourseLevel.BEGINNER.label, "Básico")
        self.assertEqual(CourseLevel.EXPERT.label, "Experto")

    def test_course_modality_valores(self):
        self.assertEqual(CourseModality.PRESENCIAL, "presencial")
        self.assertEqual(CourseModality.ONLINE, "online")
        self.assertEqual(CourseModality.HYBRID, "hybrid")

    def test_course_status_valores(self):
        self.assertEqual(CourseStatus.DRAFT, "draft")
        self.assertEqual(CourseStatus.PUBLISHED, "published")
        self.assertEqual(CourseStatus.ARCHIVED, "archived")

    def test_enrollment_mode_valores(self):
        self.assertEqual(EnrollmentMode.DIRECT, "direct")
        self.assertEqual(EnrollmentMode.APPROVAL, "approval")


class CourseViewTests(VerboseTestCase):

    def setUp(self):
        self.academy_user = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="TestPassword123!",
            is_academy=True,
        )
        self.other_academy_user = User.objects.create_user(
            username="codeacademy",
            email="info@codeacademy.com",
            password="TestPassword123!",
            is_academy=True,
        )
        self.academy = Academy.objects.create(
            owner=self.academy_user,
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
            description="Curso B2",
            status=CourseStatus.PUBLISHED,
        )

    def test_list_is_public(self):
        response = self.client.get(reverse("courses:list"))
        self.assertEqual(response.status_code, 200)

    # def test_detail_is_public(self):
    #     response = self.client.get(
    #         reverse("courses:detail", kwargs={"pk": self.course.pk, "slug": "ingles-b2"})
    #     )
    #     self.assertEqual(response.status_code, 200)

    def test_only_published_in_list(self):
        draft = Course.objects.create(
            academy=self.academy,
            category=self.category,
            title="Curso oculto",
            slug="curso-oculto",
            description="...",
            status=CourseStatus.DRAFT,
        )
        response = self.client.get(reverse("courses:list"))
        self.assertContains(response, "Inglés B2")
        self.assertNotContains(response, "Curso oculto")

    def test_create_requires_login(self):
        response = self.client.get(reverse("courses:create"))
        self.assertEqual(response.status_code, 302)

    def test_other_user_cannot_edit(self):
        self.client.force_login(self.other_academy_user)
        response = self.client.get(
            reverse("courses:update", kwargs={"pk": self.course.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_owner_can_edit(self):
        self.client.force_login(self.academy_user)
        response = self.client.get(
            reverse("courses:update", kwargs={"pk": self.course.pk})
        )
        self.assertEqual(response.status_code, 200)


class CourseSearchTests(VerboseTestCase):

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
        self.course1 = Course.objects.create(
            academy=self.academy,
            category=self.category,
            title="Inglés B2 intensivo",
            slug="ingles-b2",
            description="Curso intensivo de inglés",
            status=CourseStatus.PUBLISHED,
        )
        self.course2 = Course.objects.create(
            academy=self.academy,
            category=self.category,
            title="Francés B1",
            slug="frances-b1",
            description="Curso de francés",
            status=CourseStatus.PUBLISHED,
        )
        Convocatoria.objects.create(
            course=self.course1,
            start_date="2026-07-01",
            end_date="2026-09-30",
            price=Decimal("480.00"),
            total_places=15,
        )

    def test_search_by_title(self):
        response = self.client.get(
            reverse("courses:list"),
            {"q": "Inglés"},
        )
        self.assertContains(response, "Inglés B2 intensivo")
        self.assertNotContains(response, "Francés B1")

    def test_filter_by_category(self):
        response = self.client.get(
            reverse("courses:list"),
            {"category": "idiomas"},
        )
        self.assertEqual(response.status_code, 200)

    def test_filter_by_price_range(self):
        response = self.client.get(
            reverse("courses:list"),
            {"min_price": "400", "max_price": "600"},
        )
        self.assertContains(response, "Inglés B2 intensivo")

    def test_only_published_in_list(self):
        Course.objects.create(
            academy=self.academy,
            category=self.category,
            title="Curso borrador",
            slug="curso-borrador",
            description="...",
            status=CourseStatus.DRAFT,
        )
        response = self.client.get(reverse("courses:list"))
        self.assertContains(response, "Inglés B2 intensivo")
        self.assertNotContains(response, "Curso borrador")


class CourseFavoriteTests(VerboseTestCase):

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
        self.category = Category.objects.create(name="Idiomas", slug="idiomas")
        self.course = Course.objects.create(
            academy=self.academy,
            category=self.category,
            title="Inglés B2",
            slug="ingles-b2",
            description="...",
            status=CourseStatus.PUBLISHED,
        )

    def test_student_can_add_favorite(self):
        self.client.force_login(self.student)
        self.client.post(
            reverse("courses:toggle_favorite", kwargs={"pk": self.course.pk}),
        )
        self.assertTrue(
            CourseFavorite.objects.filter(
                user=self.student,
                course=self.course,
            ).exists()
        )

    def test_student_can_remove_favorite(self):
        CourseFavorite.objects.create(user=self.student, course=self.course)
        self.client.force_login(self.student)
        self.client.post(
            reverse("courses:toggle_favorite", kwargs={"pk": self.course.pk}),
        )
        self.assertFalse(
            CourseFavorite.objects.filter(
                user=self.student,
                course=self.course,
            ).exists()
        )

    def test_favorite_requires_login(self):
        response = self.client.post(
            reverse("courses:toggle_favorite", kwargs={"pk": self.course.pk}),
        )
        self.assertEqual(response.status_code, 302)

    def test_owner_cannot_favorite_own_course(self):
        self.client.force_login(self.owner)
        self.client.post(
            reverse("courses:toggle_favorite", kwargs={"pk": self.course.pk}),
        )
        self.assertFalse(
            CourseFavorite.objects.filter(
                user=self.owner,
                course=self.course,
            ).exists()
        )


class CourseViewsCounterTests(VerboseTestCase):

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
        self.category = Category.objects.create(name="Idiomas", slug="idiomas")
        self.course = Course.objects.create(
            academy=self.academy,
            category=self.category,
            title="Inglés B2",
            slug="ingles-b2",
            description="...",
            status=CourseStatus.PUBLISHED,
        )

    def test_course_view_increments_counter(self):
        initial = self.course.views_count
        self.client.get(self.course.get_absolute_url())
        self.course.refresh_from_db()
        self.assertEqual(self.course.views_count, initial + 1)