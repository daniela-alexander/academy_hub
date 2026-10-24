from django.contrib.auth import get_user_model
from django.db import IntegrityError
from core.test_base import VerboseTestCase

from academies.models import Academy
from courses.models import Category, Course, CourseStatus
from level_tests.models import LevelTest, LevelTestAttempt

User = get_user_model()


class LevelTestModelTests(VerboseTestCase):

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

    def test_passing_score_cannot_be_negative(self):
        with self.assertRaises(IntegrityError):
            LevelTest.objects.create(
                course=self.course,
                title="Test",
                passing_score=-1,
            )

    def test_passing_score_cannot_be_above_100(self):
        with self.assertRaises(IntegrityError):
            LevelTest.objects.create(
                course=self.course,
                title="Test",
                passing_score=101,
            )


class LevelTestAttemptModelTests(VerboseTestCase):

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
        self.level_test = LevelTest.objects.create(
            course=self.course,
            title="Test",
            passing_score=60,
        )

    def test_score_cannot_be_negative(self):
        with self.assertRaises(IntegrityError):
            LevelTestAttempt.objects.create(
                student=self.student,
                level_test=self.level_test,
                score=-1,
            )

    def test_score_cannot_be_above_100(self):
        with self.assertRaises(IntegrityError):
            LevelTestAttempt.objects.create(
                student=self.student,
                level_test=self.level_test,
                score=101,
            )