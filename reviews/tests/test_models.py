from django.contrib.auth import get_user_model
from django.db import IntegrityError
from core.test_base import VerboseTestCase

from academies.models import Academy
from courses.models import Category, Course, CourseStatus
from reviews.models import AcademyReview, CourseReview

User = get_user_model()


class CourseReviewModelTests(VerboseTestCase):

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

    def test_course_review_rating_between_1_and_5_low(self):
        with self.assertRaises(IntegrityError):
            CourseReview.objects.create(
                student=self.student,
                course=self.course,
                rating=0,
            )

    def test_course_review_rating_between_1_and_5_high(self):
        with self.assertRaises(IntegrityError):
            CourseReview.objects.create(
                student=self.student,
                course=self.course,
                rating=6,
            )


class AcademyReviewModelTests(VerboseTestCase):

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

    def test_academy_review_rating_between_1_and_5_low(self):
        with self.assertRaises(IntegrityError):
            AcademyReview.objects.create(
                student=self.student,
                academy=self.academy,
                rating=0,
            )

    def test_academy_review_rating_between_1_and_5_high(self):
        with self.assertRaises(IntegrityError):
            AcademyReview.objects.create(
                student=self.student,
                academy=self.academy,
                rating=6,
            )