from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


from .models import Academy, Teacher

User = get_user_model()


class AcademyModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="TestPassword123!",
            is_academy=True,
        )

    def test_create_academy(self):
        academy = Academy.objects.create(
            owner=self.user,
            name="English Now",
            slug="english-now",
        )

        self.assertEqual(academy.name, "English Now")
        self.assertEqual(academy.owner, self.user)
        self.assertTrue(academy.is_active)
        self.assertFalse(academy.is_verified)

    def test_academy_string_representation(self):
        academy = Academy.objects.create(
            owner=self.user,
            name="English Now",
            slug="english-now",
        )

        self.assertEqual(str(academy), "English Now")

    def test_academy_slug_is_generated(self):
        academy = Academy.objects.create(
            owner=self.user,
            name="English Now",
        )

        self.assertEqual(academy.slug, "english-now")

    def test_academy_name_must_be_unique(self):
        Academy.objects.create(
            owner=self.user,
            name="English Now",
            slug="english-now",
        )

        with self.assertRaises(Exception):
            Academy.objects.create(
                owner=self.user,
                name="English Now",
                slug="english-now-2",
            )

    def test_user_can_have_multiple_academies(self):
        academy1 = Academy.objects.create(
            owner=self.user,
            name="English Now",
            slug="english-now",
        )

        academy2 = Academy.objects.create(
            owner=self.user,
            name="Code Academy",
            slug="code-academy",
        )

        self.assertEqual(self.user.academies.count(), 2)
        self.assertIn(academy1, self.user.academies.all())
        self.assertIn(academy2, self.user.academies.all())


class TeacherModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="TestPassword123!",
            is_academy=True,
        )

        self.academy = Academy.objects.create(
            owner=self.user,
            name="English Now",
            slug="english-now",
        )

    def test_create_teacher(self):
        teacher = Teacher.objects.create(
            academy=self.academy,
            first_name="Laura",
            last_name="García",
            specialty="Inglés",
        )

        self.assertEqual(teacher.first_name, "Laura")
        self.assertEqual(teacher.academy, self.academy)
        self.assertTrue(teacher.is_active)

    def test_teacher_string_representation(self):
        teacher = Teacher.objects.create(
            academy=self.academy,
            first_name="Laura",
            last_name="García",
        )

        self.assertEqual(str(teacher), "Laura García")

    def test_academy_can_have_teachers(self):
        teacher1 = Teacher.objects.create(
            academy=self.academy,
            first_name="Laura",
        )

        teacher2 = Teacher.objects.create(
            academy=self.academy,
            first_name="Carlos",
        )

        self.assertEqual(self.academy.teachers.count(), 2)
        self.assertIn(teacher1, self.academy.teachers.all())
        self.assertIn(teacher2, self.academy.teachers.all())
class AcademyViewTests(TestCase):
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
    def test_academy_list_is_public(self):
        response = self.client.get(reverse("academies:list"))
        self.assertEqual(response.status_code, 200)
    def test_academy_detail_is_public(self):
        response = self.client.get(
            reverse("academies:detail", kwargs={"slug": "english-now"})
        )
        self.assertEqual(response.status_code, 200)
    def test_create_requires_login(self):
        response = self.client.get(reverse("academies:create"))
        self.assertEqual(response.status_code, 302)
    def test_other_user_cannot_edit(self):
        self.client.force_login(self.other)
        response = self.client.get(
            reverse("academies:update", kwargs={"slug": "english-now"})
        )
        self.assertEqual(response.status_code, 403)
    def test_owner_can_edit(self):
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse("academies:update", kwargs={"slug": "english-now"})
        )
        self.assertEqual(response.status_code, 200)

