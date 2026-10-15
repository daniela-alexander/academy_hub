from django.contrib.auth import get_user_model
from django.test import TestCase
from core.test_base import VerboseTestCase
from django.urls import reverse

from academies.models import Academy
from courses.models import Category, Course, CourseStatus

from .models import AcademyReview, CourseReview


User = get_user_model()


class CourseReviewTests(VerboseTestCase):
    def setUp(self):
        self.academy_user = User.objects.create_user(
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
            owner=self.academy_user, name="English Now", slug="english-now"
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

    def test_student_can_create_review(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("reviews:course_create", kwargs={"course_pk": self.course.pk}),
            {"rating": 5, "comment": "Excelente"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CourseReview.objects.count(), 1)

    def test_student_cannot_review_twice(self):
        self.client.force_login(self.student)

        self.client.post(
            reverse("reviews:course_create", kwargs={"course_pk": self.course.pk}),
            {"rating": 5, "comment": "Excelente"},
        )

        response = self.client.post(
            reverse("reviews:course_create", kwargs={"course_pk": self.course.pk}),
            {"rating": 3, "comment": "Otra"},
        )

        self.assertEqual(CourseReview.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_review_requires_login(self):
        response = self.client.post(
            reverse("reviews:course_create", kwargs={"course_pk": self.course.pk}),
            {"rating": 5},
        )
        self.assertEqual(response.status_code, 302)

class CourseReviewListTests(TestCase):
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
        CourseReview.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
        comment="Excelente",
        )
    def test_review_list_is_public(self):
        response = self.client.get(reverse("reviews:course_review_list"))
        self.assertEqual(response.status_code, 200)
    def test_filter_by_rating(self):
        response = self.client.get(
            reverse("reviews:course_review_list"),
            {"rating": "5"},
        )
        self.assertContains(response, "Excelente")



def test_my_reviews_filter_by_rating(self):
    self.client.force_login(self.student)
    CourseReview.objects.create(
        student=self.student, course=self.course, rating=5,
    )
    CourseReview.objects.create(
        student=self.student, course=self.course2, rating=2,
    )
    response = self.client.get(
        reverse("reviews:mine"),
        {"rating": "5"},
    )
    self.assertContains(response, "5/5")