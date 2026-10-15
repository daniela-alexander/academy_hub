from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.urls import reverse
from django.utils.text import slugify

from academies.models import Academy, Teacher
from core.test_base import VerboseTestCase

from decimal import Decimal

from academies.models import Academy
from .models import (
    Category,
    Course,
    CourseImage,
    CourseLevel,
    CourseModality,
    CourseStatus,
    EnrollmentMode,
    Convocatoria,
    CourseFavorite,
)

User = get_user_model()


# =============================================================================
# Helpers
# =============================================================================
def crear_usuario(username="owner1"):
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="testpass123",
    )


# =============================================================================
# TESTS: Category
# =============================================================================
class CategoryModelTest(VerboseTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Idiomas",
            description="Cursos de idiomas",
            icon="book",
        )

    # ---------- Creación ----------
    def test_creacion_correcta(self):
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(self.category.name, "Idiomas")
        self.assertEqual(self.category.description, "Cursos de idiomas")
        self.assertEqual(self.category.icon, "book")

    def test_slug_se_genera_automaticamente(self):
        self.assertEqual(self.category.slug, "idiomas")

    def test_slug_no_se_sobrescribe_si_ya_existe(self):
        c = Category.objects.create(name="Programación", slug="prog-custom")
        self.assertEqual(c.slug, "prog-custom")

    def test_is_active_por_defecto(self):
        self.assertTrue(self.category.is_active)

    def test_created_at_se_rellena(self):
        self.assertIsNotNone(self.category.created_at)

    def test_description_e_icon_opcionales(self):
        c = Category.objects.create(name="Sin extras")
        self.assertEqual(c.description, "")
        self.assertEqual(c.icon, "")

    # ---------- __str__ ----------
    def test_str_devuelve_name(self):
        self.assertEqual(str(self.category), "Idiomas")

    # ---------- Restricciones ----------
    def test_name_es_unico(self):
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Idiomas")

    def test_slug_es_unico(self):
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Otro", slug="idiomas")

    def test_name_requerido(self):
        c = Category(name="")
        with self.assertRaises(ValidationError):
            c.full_clean()

    # ---------- Ordenación ----------
    def test_ordering_por_name(self):
        Category.objects.create(name="Zzz")
        Category.objects.create(name="Aaa")
        nombres = list(Category.objects.values_list("name", flat=True))
        self.assertEqual(nombres, sorted(nombres))

    # ---------- Meta ----------
    def test_verbose_names(self):
        self.assertEqual(Category._meta.verbose_name, "Categoría")
        self.assertEqual(Category._meta.verbose_name_plural, "Categorías")


# =============================================================================
# TESTS: TextChoices
# =============================================================================
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


# =============================================================================
# TESTS: Course
# =============================================================================
class CourseModelTest(VerboseTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = crear_usuario("owner_course")
        cls.academy = Academy.objects.create(
            owner=cls.user, name="Academia Cursos",
        )
        cls.teacher = Teacher.objects.create(
            academy=cls.academy,
            first_name="Ana",
            last_name="García",
        )
        cls.category = Category.objects.create(name="Informática")

    def _crear_curso(self, **kwargs):
        defaults = dict(
            academy=self.academy,
            category=self.category,
            title="Curso de Python",
            description="Aprende Python desde cero",
        )
        defaults.update(kwargs)
        return Course.objects.create(**defaults)

    # ---------- Creación ----------
    def test_creacion_correcta(self):
        curso = self._crear_curso()
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(curso.title, "Curso de Python")
        self.assertEqual(curso.academy, self.academy)
        self.assertEqual(curso.category, self.category)

    def test_valores_por_defecto(self):
        curso = self._crear_curso()
        self.assertEqual(curso.level, CourseLevel.BEGINNER)
        self.assertEqual(curso.modality, CourseModality.PRESENCIAL)
        self.assertEqual(curso.status, CourseStatus.PUBLISHED)
        self.assertEqual(curso.enrollment_mode, EnrollmentMode.DIRECT)
        self.assertFalse(curso.requires_level_test)
        self.assertFalse(curso.is_negotiable)
        self.assertEqual(curso.duration_hours, 0)
        self.assertEqual(curso.views_count, 0)

    def test_teacher_es_opcional(self):
        curso = self._crear_curso()
        self.assertIsNone(curso.teacher)

    def test_teacher_asignado(self):
        curso = self._crear_curso(teacher=self.teacher)
        self.assertEqual(curso.teacher, self.teacher)

    def test_campos_texto_opcionales_vacios(self):
        curso = self._crear_curso()
        self.assertEqual(curso.objectives, "")
        self.assertEqual(curso.competences, "")
        self.assertEqual(curso.requirements, "")

    # ---------- Slug ----------
    def test_slug_se_genera_automaticamente(self):
        curso = self._crear_curso(title="Curso de Django Avanzado")
        self.assertEqual(curso.slug, slugify("Curso de Django Avanzado"))

    def test_slug_no_se_sobrescribe(self):
        curso = self._crear_curso(title="Curso X", slug="slug-custom")
        self.assertEqual(curso.slug, "slug-custom")

    # ---------- Timestamps ----------
    def test_created_at_y_updated_at(self):
        curso = self._crear_curso()
        self.assertIsNotNone(curso.created_at)
        self.assertIsNotNone(curso.updated_at)
        self.assertEqual(curso.created_at, curso.updated_at)

    # ---------- __str__ ----------
    def test_str_devuelve_title(self):
        curso = self._crear_curso(title="Curso de Inglés")
        self.assertEqual(str(curso), "Curso de Inglés")

    # ---------- Propiedades ----------
    def test_is_published_true(self):
        curso = self._crear_curso(status=CourseStatus.PUBLISHED)
        self.assertTrue(curso.is_published)

    def test_is_published_false(self):
        curso = self._crear_curso(status=CourseStatus.DRAFT)
        self.assertFalse(curso.is_published)

    def test_has_convocatorias_devuelve_false_sin_convocatorias(self):
        curso = self._crear_curso()
        self.assertFalse(curso.has_convocatorias)

    def test_primary_image_sin_imagenes(self):
        curso = self._crear_curso()
        self.assertIsNone(curso.primary_image)

    def test_primary_image_devuelve_la_marcada_como_primary(self):
        curso = self._crear_curso()
        CourseImage.objects.create(
            course=curso, image="courses/a.jpg", is_primary=False,
        )
        img2 = CourseImage.objects.create(
            course=curso, image="courses/b.jpg", is_primary=True,
        )
        self.assertEqual(curso.primary_image, img2)

    def test_primary_image_devuelve_la_primera_si_no_hay_primary(self):
        curso = self._crear_curso()
        img1 = CourseImage.objects.create(
            course=curso, image="courses/a.jpg", is_primary=False, position=0,
        )
        CourseImage.objects.create(
            course=curso, image="courses/b.jpg", is_primary=False, position=1,
        )
        self.assertEqual(curso.primary_image, img1)

    # ---------- Choices / validación ----------
    def test_level_invalido_lanza_error(self):
        curso = self._crear_curso(level="inventado")
        with self.assertRaises(ValidationError):
            curso.full_clean()

    def test_modality_invalida_lanza_error(self):
        curso = self._crear_curso(modality="inventada")
        with self.assertRaises(ValidationError):
            curso.full_clean()

    def test_status_invalido_lanza_error(self):
        curso = self._crear_curso(status="inventado")
        with self.assertRaises(ValidationError):
            curso.full_clean()

    def test_enrollment_mode_invalido_lanza_error(self):
        curso = self._crear_curso(enrollment_mode="inventado")
        with self.assertRaises(ValidationError):
            curso.full_clean()

    # ---------- Campos requeridos ----------
    def test_title_requerido(self):
        curso = Course(
            academy=self.academy,
            category=self.category,
            title="",
            description="algo",
        )
        with self.assertRaises(ValidationError):
            curso.full_clean()

    def test_description_requerida(self):
        curso = Course(
            academy=self.academy,
            category=self.category,
            title="Curso",
            description="",
        )
        with self.assertRaises(ValidationError):
            curso.full_clean()

    # ---------- Relaciones / on_delete ----------
    def test_academy_cascade_delete(self):
        curso = self._crear_curso()
        pk = curso.pk
        self.academy.delete()
        self.assertFalse(Course.objects.filter(pk=pk).exists())

    def test_category_protect_delete(self):
        self._crear_curso()
        with self.assertRaises(ProtectedError):
            self.category.delete()

    def test_teacher_set_null_al_borrar(self):
        curso = self._crear_curso(teacher=self.teacher)
        self.teacher.delete()
        curso.refresh_from_db()
        self.assertIsNone(curso.teacher)

    # ---------- Related names ----------
    def test_related_name_academy_courses(self):
        curso = self._crear_curso()
        self.assertIn(curso, self.academy.courses.all())

    def test_related_name_category_courses(self):
        curso = self._crear_curso()
        self.assertIn(curso, self.category.courses.all())

    def test_related_name_teacher_courses(self):
        curso = self._crear_curso(teacher=self.teacher)
        self.assertIn(curso, self.teacher.courses.all())

    # ---------- Ordenación ----------
    def test_ordering_por_created_at_descendente(self):
        c1 = self._crear_curso(title="Primero")
        c2 = self._crear_curso(title="Segundo")
        cursos = list(Course.objects.all())
        self.assertEqual(cursos[0], c2)
        self.assertEqual(cursos[1], c1)

    # ---------- Meta ----------
    def test_verbose_names(self):
        self.assertEqual(Course._meta.verbose_name, "Curso")
        self.assertEqual(Course._meta.verbose_name_plural, "Cursos")

    def test_indexes_definidos(self):
        index_fields = [tuple(idx.fields) for idx in Course._meta.indexes]
        self.assertIn(("status",), index_fields)
        self.assertIn(("created_at",), index_fields)
        self.assertIn(("level",), index_fields)
        self.assertIn(("modality",), index_fields)
        self.assertIn(("category",), index_fields)
        self.assertIn(("academy",), index_fields)


# =============================================================================
# TESTS: CourseImage
# =============================================================================
class CourseImageModelTest(VerboseTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = crear_usuario("owner_img")
        cls.academy = Academy.objects.create(
            owner=cls.user, name="Academia Img",
        )
        cls.category = Category.objects.create(name="Música")
        cls.course = Course.objects.create(
            academy=cls.academy,
            category=cls.category,
            title="Curso de Piano",
            description="Aprende piano",
        )

    # ---------- Creación ----------
    def test_creacion_correcta(self):
        img = CourseImage.objects.create(
            course=self.course,
            image="courses/piano.jpg",
            alt_text="Piano de cola",
            is_primary=True,
            position=1,
        )
        self.assertEqual(CourseImage.objects.count(), 1)
        self.assertEqual(img.course, self.course)
        self.assertEqual(img.alt_text, "Piano de cola")
        self.assertTrue(img.is_primary)
        self.assertEqual(img.position, 1)

    def test_valores_por_defecto(self):
        img = CourseImage.objects.create(
            course=self.course, image="courses/x.jpg",
        )
        self.assertFalse(img.is_primary)
        self.assertEqual(img.position, 0)
        self.assertEqual(img.alt_text, "")
        self.assertIsNotNone(img.created_at)

    # ---------- __str__ ----------
    def test_str(self):
        img = CourseImage.objects.create(
            course=self.course, image="courses/x.jpg",
        )
        self.assertEqual(str(img), "Imagen de Curso de Piano")

    # ---------- Relaciones ----------
    def test_related_name_images(self):
        img = CourseImage.objects.create(
            course=self.course, image="courses/x.jpg",
        )
        self.assertIn(img, self.course.images.all())

    def test_cascade_delete_desde_course(self):
        CourseImage.objects.create(
            course=self.course, image="courses/x.jpg",
        )
        self.assertEqual(CourseImage.objects.count(), 1)
        self.course.delete()
        self.assertEqual(CourseImage.objects.count(), 0)

    # ---------- Ordenación ----------
    def test_ordering_por_position_y_created_at(self):
        img_a = CourseImage.objects.create(
            course=self.course, image="courses/a.jpg", position=2,
        )
        img_b = CourseImage.objects.create(
            course=self.course, image="courses/b.jpg", position=1,
        )
        imagenes = list(CourseImage.objects.all())
        self.assertEqual(imagenes[0], img_b)
        self.assertEqual(imagenes[1], img_a)

    # ---------- Meta ----------
    def test_verbose_names(self):
        self.assertEqual(CourseImage._meta.verbose_name, "Imagen de curso")
        self.assertEqual(
            CourseImage._meta.verbose_name_plural, "Imágenes de curso"
        )

    def test_index_definido(self):
        index_fields = [tuple(idx.fields) for idx in CourseImage._meta.indexes]
        self.assertIn(("course", "is_primary"), index_fields)


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