from django.contrib.auth import get_user_model
from django.test import TestCase

from academies.models import Academy
from courses.models import Category, Course, CourseStatus
from courses.services import archive_course

User = get_user_model()


class ArchiveCourseTests(TestCase):

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
        self.category = Category.objects.create(
            name="Idiomas",
            slug="idiomas",
        )
        self.course = Course.objects.create(
            academy=self.academy,
            category=self.category,
            title="Inglés B2",
            slug="ingles-b2",
            description="...",
            status=CourseStatus.PUBLISHED,
        )

    def test_owner_can_archive_course(self):
        archive_course(self.course.pk, self.owner)
        self.course.refresh_from_db()
        self.assertEqual(self.course.status, CourseStatus.ARCHIVED)

    def test_other_user_cannot_archive_course(self):
        with self.assertRaises(ValueError):
            archive_course(self.course.pk, self.other)