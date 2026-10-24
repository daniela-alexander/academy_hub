from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

from academies.models import Academy
from core.test_base import VerboseTestCase
from courses.models import (
    Category,
    Convocatoria,
    Course,
    CourseModality,
    CourseStatus,
)
from enrollments.models import (
    Enrollment,
    EnrollmentAnswer,
    EnrollmentDocument,
    EnrollmentStatus,
    PaymentStatus,
    WaitlistEntry,
)

User = get_user_model()



class EnrollmentBaseTestCase(VerboseTestCase):
    """
    Clase base con los datos mínimos compartidos por todos los tests.
    Se encarga de crear usuario, academia, categoría, curso y convocatoria.
    """

    def setUp(self):
        # Usuario academia
        self.academy_user = User.objects.create_user(
            username="englishnow",
            email="info@englishnow.com",
            password="TestPassword123!",
            is_academy=True,
        )

        # Usuario alumno
        self.student = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )

        # Academia
        self.academy = Academy.objects.create(
            owner=self.academy_user,
            name="English Now",
            slug="english-now",
        )

        # Categoría
        self.category = Category.objects.create(
            name="Idiomas",
            slug="idiomas",
        )

        # Curso
        self.course = Course.objects.create(
            academy=self.academy,
            category=self.category,
            title="Inglés B2 intensivo",
            slug="ingles-b2-intensivo",
            description="Curso intensivo de preparación del B2.",
            status=CourseStatus.PUBLISHED,
        )

        # Convocatoria
        self.convocatoria = Convocatoria.objects.create(
            course=self.course,
            name="Verano 2026",
            start_date=timezone.now().date() + timedelta(days=30),
            end_date=timezone.now().date() + timedelta(days=120),
            enrollment_deadline=timezone.now().date() + timedelta(days=20),
            modality=CourseModality.PRESENCIAL,
            price=Decimal("480.00"),
            deposit=Decimal("50.00"),
            total_places=15,
            reserved_places=0,
            enrolled_places=0,
        )


class EnrollmentRelationsTests(EnrollmentBaseTestCase):
    """
    Comprobamos que los related_name funcionan.
    """

    def test_student_enrollments_reverse_relation(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        self.assertIn(
            enrollment,
            self.student.enrollments.all(),
        )

    def test_convocatoria_enrollments_reverse_relation(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        self.assertIn(
            enrollment,
            self.convocatoria.enrollments.all(),
        )

    def test_student_waitlist_entries_reverse_relation(self):
        entry = WaitlistEntry.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        self.assertIn(
            entry,
            self.student.waitlist_entries.all(),
        )

    def test_convocatoria_waitlist_reverse_relation(self):
        entry = WaitlistEntry.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        self.assertIn(
            entry,
            self.convocatoria.waitlist_entries.all(),
        )

    def test_enrollment_answers_reverse_relation(self):
        answer = EnrollmentAnswer.objects.create(
            enrollment=Enrollment.objects.create(
                student=self.student,
                convocatoria=self.convocatoria,
            ),
            question_key="motivation",
            question_text="¿Por qué?",
            answer_text="Trabajo",
        )

        self.assertIn(
            answer,
            answer.enrollment.answers.all(),
        )

    def test_enrollment_documents_reverse_relation(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        document = EnrollmentDocument.objects.create(
            enrollment=enrollment,
            name="DNI",
            file="enrollments/documents/dni.pdf",
        )

        self.assertIn(
            document,
            enrollment.documents.all(),
        )

    def test_deleting_enrollment_deletes_answers(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        EnrollmentAnswer.objects.create(
            enrollment=enrollment,
            question_key="motivation",
            question_text="¿Por qué?",
            answer_text="Trabajo",
        )

        self.assertEqual(
            EnrollmentAnswer.objects.count(),
            1,
        )

        enrollment.delete()

        self.assertEqual(
            EnrollmentAnswer.objects.count(),
            0,
        )

    def test_deleting_enrollment_deletes_documents(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        EnrollmentDocument.objects.create(
            enrollment=enrollment,
            name="DNI",
            file="enrollments/documents/dni.pdf",
        )

        self.assertEqual(
            EnrollmentDocument.objects.count(),
            1,
        )

        enrollment.delete()

        self.assertEqual(
            EnrollmentDocument.objects.count(),
            0,
        )


class EnrollmentViewTests(EnrollmentBaseTestCase):

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
            description="...",
        )
        self.convocatoria = Convocatoria.objects.create(
            course=self.course,
            name="Verano",
            start_date=timezone.now().date() + timedelta(days=30),
            end_date=timezone.now().date() + timedelta(days=90),
            price=Decimal("480.00"),
            total_places=15,
        )

    def test_student_can_enroll(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("enrollments:create", kwargs={"convocatoria_pk": self.convocatoria.pk}),
            {},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Enrollment.objects.count(), 1)

    def test_enrollment_requires_login(self):
        response = self.client.post(
            reverse("enrollments:create", kwargs={"convocatoria_pk": self.convocatoria.pk}),
            {},
        )
        self.assertEqual(response.status_code, 302)

    def test_other_user_cannot_see_enrollment(self):
        other_student = User.objects.create_user(
            username="carlos",
            email="carlos@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.client.force_login(self.student)
        self.client.post(
            reverse("enrollments:create", kwargs={"convocatoria_pk": self.convocatoria.pk}),
            {},
        )
        enrollment = Enrollment.objects.first()
        self.client.force_login(other_student)
        response = self.client.get(reverse("enrollments:detail", kwargs={"pk": enrollment.pk}))
        self.assertEqual(response.status_code, 403)

    def test_academy_can_approve(self):
        self.client.force_login(self.student)
        self.client.post(
            reverse("enrollments:create", kwargs={"convocatoria_pk": self.convocatoria.pk}),
            {},
        )
        enrollment = Enrollment.objects.first()
        self.client.force_login(self.academy_user)
        response = self.client.post(
            reverse("enrollments:approve", kwargs={"pk": enrollment.pk}),
            {},
        )
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, EnrollmentStatus.APPROVED)


class AcademyEnrollmentListTests(VerboseTestCase):

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
            owner=self.academy_user,
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
        )
        self.convocatoria = Convocatoria.objects.create(
            course=self.course,
            start_date="2026-07-01",
            end_date="2026-09-30",
            price=Decimal("480.00"),
            total_places=15,
        )

    def test_academy_sees_own_enrollments(self):
        Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )
        self.client.force_login(self.academy_user)
        response = self.client.get(reverse("enrollments:academy_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "laura")

    def test_filter_by_status(self):
        Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
            status=EnrollmentStatus.PENDING,
        )
        self.client.force_login(self.academy_user)
        response = self.client.get(
            reverse("enrollments:academy_list"),
            {"status": "pending"},
        )
        self.assertEqual(response.status_code, 200)

    def test_academy_enrollments_paginadas(self):
        self.client.force_login(self.academy_user)

        for i in range(25):
            student = User.objects.create_user(
                username=f"student{i}",
                email=f"student{i}@example.com",
                password="TestPassword123!",
                is_student=True,
            )
            Enrollment.objects.create(
                student=student,
                convocatoria=self.convocatoria,
            )

        response = self.client.get(reverse("enrollments:academy_list"))
        self.assertEqual(len(response.context["enrollments"]), 20)

class EnrollmentStatusChoicesTests(VerboseTestCase):
    """
    Los choices son strings controlados.
    Comprobamos que los valores esperados existen.
    """

    def test_enrollment_status_values(self):
        self.assertEqual(EnrollmentStatus.PENDING, "pending")
        self.assertEqual(EnrollmentStatus.APPROVED, "approved")
        self.assertEqual(EnrollmentStatus.REJECTED, "rejected")
        self.assertEqual(EnrollmentStatus.RESERVED, "reserved")
        self.assertEqual(
            EnrollmentStatus.RESERVATION_EXPIRED,
            "reservation_expired",
        )
        self.assertEqual(EnrollmentStatus.ENROLLED, "enrolled")
        self.assertEqual(EnrollmentStatus.WAITLIST, "waitlist")
        self.assertEqual(EnrollmentStatus.CANCELLED, "cancelled")
        self.assertEqual(EnrollmentStatus.COMPLETED, "completed")

    def test_payment_status_values(self):
        self.assertEqual(PaymentStatus.PENDING, "pending")
        self.assertEqual(PaymentStatus.PARTIAL, "partial")
        self.assertEqual(PaymentStatus.PAID, "paid")
        self.assertEqual(PaymentStatus.REFUNDED, "refunded")
        self.assertEqual(PaymentStatus.FAILED, "failed")

