from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone

from academies.models import Academy
from core.test_base import VerboseTestCase
from courses.models import (
    Category,
    Convocatoria,
    Course,
    CourseModality,
    CourseStatus,
)
from .models import (
    Enrollment,
    EnrollmentAnswer,
    EnrollmentDocument,
    EnrollmentStatus,
    PaymentStatus,
    WaitlistEntry,
)

User = get_user_model()


# ============================================================
# FIXTURES COMUNES
# ============================================================

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


# ============================================================
# TESTS DE CHOICES
# ============================================================

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


# ============================================================
# TESTS DE ENROLLMENT
# ============================================================

class EnrollmentModelTests(EnrollmentBaseTestCase):
    """
    Tests del modelo principal: Enrollment.
    """

    def test_create_enrollment(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.convocatoria, self.convocatoria)
        self.assertEqual(
            enrollment.status,
            EnrollmentStatus.PENDING,
        )
        self.assertEqual(
            enrollment.payment_status,
            PaymentStatus.PENDING,
        )
        self.assertEqual(enrollment.amount_paid, Decimal("0.00"))
        self.assertEqual(enrollment.discount_amount, Decimal("0.00"))

    def test_enrollment_string_representation(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        expected = f"{self.student.username} → {self.convocatoria}"
        self.assertEqual(str(enrollment), expected)

    def test_enrollment_default_status_is_pending(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        self.assertEqual(
            enrollment.status,
            EnrollmentStatus.PENDING,
        )

    def test_enrollment_default_payment_status_is_pending(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        self.assertEqual(
            enrollment.payment_status,
            PaymentStatus.PENDING,
        )

    def test_student_cannot_enroll_twice_in_same_convocatoria(self):
        """
        La UniqueConstraint debe impedir duplicados.
        """
        Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(
                student=self.student,
                convocatoria=self.convocatoria,
            )

    def test_different_students_can_enroll_in_same_convocatoria(self):
        other_student = User.objects.create_user(
            username="carlos",
            email="carlos@example.com",
            password="TestPassword123!",
            is_student=True,
        )

        enrollment1 = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        enrollment2 = Enrollment.objects.create(
            student=other_student,
            convocatoria=self.convocatoria,
        )

        self.assertEqual(
            self.convocatoria.enrollments.count(),
            2,
        )
        self.assertIn(enrollment1, self.convocatoria.enrollments.all())
        self.assertIn(enrollment2, self.convocatoria.enrollments.all())

    def test_same_student_can_enroll_in_different_convocatorias(self):
        other_convocatoria = Convocatoria.objects.create(
            course=self.course,
            name="Otoño 2026",
            start_date=timezone.now().date() + timedelta(days=180),
            end_date=timezone.now().date() + timedelta(days=270),
            price=Decimal("450.00"),
            total_places=10,
        )

        enrollment1 = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        enrollment2 = Enrollment.objects.create(
            student=self.student,
            convocatoria=other_convocatoria,
        )

        self.assertEqual(
            self.student.enrollments.count(),
            2,
        )
        self.assertIn(enrollment1, self.student.enrollments.all())
        self.assertIn(enrollment2, self.student.enrollments.all())

    def test_is_active_property(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        # PENDING → activo
        self.assertTrue(enrollment.is_active)

        # ENROLLED → activo
        enrollment.status = EnrollmentStatus.ENROLLED
        self.assertTrue(enrollment.is_active)

        # REJECTED → inactivo
        enrollment.status = EnrollmentStatus.REJECTED
        self.assertFalse(enrollment.is_active)

        # CANCELLED → inactivo
        enrollment.status = EnrollmentStatus.CANCELLED
        self.assertFalse(enrollment.is_active)

        # COMPLETED → inactivo
        enrollment.status = EnrollmentStatus.COMPLETED
        self.assertFalse(enrollment.is_active)

    def test_is_reservation_expired_property(self):
        # Sin fecha de caducidad → no está expirada
        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )
        self.assertFalse(enrollment.is_reservation_expired)

        # Con fecha de caducidad futura → no está expirada
        enrollment.reservation_expires_at = (
            timezone.now() + timedelta(days=5)
        )
        self.assertFalse(enrollment.is_reservation_expired)

        # Con fecha de caducidad pasada → está expirada
        enrollment.reservation_expires_at = (
            timezone.now() - timedelta(days=1)
        )
        self.assertTrue(enrollment.is_reservation_expired)

    def test_total_price_property(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
            discount_amount=Decimal("80.00"),
        )

        # 480 - 80 = 400
        self.assertEqual(
            enrollment.total_price,
            Decimal("400.00"),
        )

    def test_total_price_without_discount(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        self.assertEqual(
            enrollment.total_price,
            Decimal("480.00"),
        )

    def test_pending_amount_property(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
            amount_paid=Decimal("150.00"),
        )

        # 480 - 150 = 330
        self.assertEqual(
            enrollment.pending_amount,
            Decimal("330.00"),
        )

    def test_pending_amount_cannot_be_negative(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
            amount_paid=Decimal("600.00"),
        )

        # Ha pagado más que el precio → pendiente 0, no negativo
        self.assertEqual(
            enrollment.pending_amount,
            Decimal("0.00"),
        )

    def test_pending_amount_with_discount(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
            amount_paid=Decimal("200.00"),
            discount_amount=Decimal("100.00"),
        )

        # total_price = 380, pagado 200 → pendiente 180
        self.assertEqual(
            enrollment.pending_amount,
            Decimal("180.00"),
        )

    def test_ordering_is_recent_first(self):
        enrollment1 = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        other_student = User.objects.create_user(
            username="carlos",
            email="carlos@example.com",
            password="TestPassword123!",
            is_student=True,
        )

        enrollment2 = Enrollment.objects.create(
            student=other_student,
            convocatoria=self.convocatoria,
        )

        enrollments = list(Enrollment.objects.all())
        self.assertEqual(enrollments[0], enrollment2)
        self.assertEqual(enrollments[1], enrollment1)


# ============================================================
# TESTS DE WAITLISTENTRY
# ============================================================

class WaitlistEntryModelTests(EnrollmentBaseTestCase):
    """
    Tests de la lista de espera.
    """

    def test_create_waitlist_entry(self):
        entry = WaitlistEntry.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
            position=1,
        )

        self.assertEqual(entry.student, self.student)
        self.assertEqual(entry.convocatoria, self.convocatoria)
        self.assertEqual(entry.position, 1)
        self.assertFalse(entry.is_notified)
        self.assertIsNone(entry.converted_to_enrollment)

    def test_waitlist_string_representation(self):
        entry = WaitlistEntry.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
            position=3,
        )

        expected = f"#3 {self.student.username} → {self.convocatoria}"
        self.assertEqual(str(entry), expected)

    def test_student_cannot_be_twice_in_waitlist(self):
        WaitlistEntry.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
            position=1,
        )

        with self.assertRaises(IntegrityError):
            WaitlistEntry.objects.create(
                student=self.student,
                convocatoria=self.convocatoria,
                position=2,
            )

    def test_convocatoria_can_have_multiple_waitlist_entries(self):
        other_student = User.objects.create_user(
            username="carlos",
            email="carlos@example.com",
            password="TestPassword123!",
            is_student=True,
        )

        entry1 = WaitlistEntry.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
            position=1,
        )

        entry2 = WaitlistEntry.objects.create(
            student=other_student,
            convocatoria=self.convocatoria,
            position=2,
        )

        self.assertEqual(
            self.convocatoria.waitlist_entries.count(),
            2,
        )
        self.assertIn(entry1, self.convocatoria.waitlist_entries.all())
        self.assertIn(entry2, self.convocatoria.waitlist_entries.all())

    def test_waitlist_entry_can_convert_to_enrollment(self):
        entry = WaitlistEntry.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
            position=1,
        )

        enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

        entry.converted_to_enrollment = enrollment
        entry.is_notified = True
        entry.notified_at = timezone.now()
        entry.save()

        entry.refresh_from_db()

        self.assertEqual(entry.converted_to_enrollment, enrollment)
        self.assertTrue(entry.is_notified)
        self.assertIsNotNone(entry.notified_at)

    def test_ordering_is_by_position(self):
        other_student = User.objects.create_user(
            username="carlos",
            email="carlos@example.com",
            password="TestPassword123!",
            is_student=True,
        )

        third_student = User.objects.create_user(
            username="ana",
            email="ana@example.com",
            password="TestPassword123!",
            is_student=True,
        )

        entry2 = WaitlistEntry.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
            position=2,
        )

        entry1 = WaitlistEntry.objects.create(
            student=other_student,
            convocatoria=self.convocatoria,
            position=1,
        )

        entry3 = WaitlistEntry.objects.create(
            student=third_student,
            convocatoria=self.convocatoria,
            position=3,
        )

        entries = list(
            WaitlistEntry.objects.filter(
                convocatoria=self.convocatoria
            )
        )

        self.assertEqual(entries[0], entry1)
        self.assertEqual(entries[1], entry2)
        self.assertEqual(entries[2], entry3)


# ============================================================
# TESTS DE ENROLLMENTANSWER
# ============================================================

class EnrollmentAnswerModelTests(EnrollmentBaseTestCase):
    """
    Tests de las respuestas del formulario de inscripción.
    """

    def setUp(self):
        super().setUp()

        self.enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

    def test_create_answer(self):
        answer = EnrollmentAnswer.objects.create(
            enrollment=self.enrollment,
            question_key="motivation",
            question_text="¿Por qué quieres hacer este curso?",
            answer_text="Para mejorar mi inglés de cara al trabajo.",
        )

        self.assertEqual(
            answer.question_key,
            "motivation",
        )
        self.assertEqual(
            answer.answer_text,
            "Para mejorar mi inglés de cara al trabajo.",
        )

    def test_answer_string_representation(self):
        answer = EnrollmentAnswer.objects.create(
            enrollment=self.enrollment,
            question_key="motivation",
            question_text="¿Por qué quieres hacer este curso?",
            answer_text="Para mejorar mi inglés.",
        )

        expected = "motivation: Para mejorar mi inglés."
        self.assertEqual(str(answer), expected)

    def test_enrollment_can_have_multiple_answers(self):
        EnrollmentAnswer.objects.create(
            enrollment=self.enrollment,
            question_key="motivation",
            question_text="¿Por qué?",
            answer_text="Trabajo",
        )

        EnrollmentAnswer.objects.create(
            enrollment=self.enrollment,
            question_key="level",
            question_text="¿Nivel actual?",
            answer_text="B1",
        )

        self.assertEqual(
            self.enrollment.answers.count(),
            2,
        )

    def test_answer_can_be_empty(self):
        answer = EnrollmentAnswer.objects.create(
            enrollment=self.enrollment,
            question_key="optional",
            question_text="Pregunta opcional",
        )

        self.assertEqual(answer.answer_text, "")


# ============================================================
# TESTS DE ENROLLMENTDOCUMENT
# ============================================================

class EnrollmentDocumentModelTests(EnrollmentBaseTestCase):
    """
    Tests de los documentos adjuntos a una inscripción.
    """

    def setUp(self):
        super().setUp()

        self.enrollment = Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )

    def test_create_document(self):
        document = EnrollmentDocument.objects.create(
            enrollment=self.enrollment,
            name="DNI",
            file="enrollments/documents/dni.pdf",
        )

        self.assertEqual(document.name, "DNI")
        self.assertEqual(
            document.file.name,
            "enrollments/documents/dni.pdf",
        )
        self.assertFalse(document.is_verified)

    def test_document_string_representation(self):
        document = EnrollmentDocument.objects.create(
            enrollment=self.enrollment,
            name="DNI",
            file="enrollments/documents/dni.pdf",
        )

        expected = f"DNI ({self.enrollment})"
        self.assertEqual(str(document), expected)

    def test_enrollment_can_have_multiple_documents(self):
        EnrollmentDocument.objects.create(
            enrollment=self.enrollment,
            name="DNI",
            file="enrollments/documents/dni.pdf",
        )

        EnrollmentDocument.objects.create(
            enrollment=self.enrollment,
            name="Título",
            file="enrollments/documents/titulo.pdf",
        )

        self.assertEqual(
            self.enrollment.documents.count(),
            2,
        )

    def test_document_can_be_verified(self):
        document = EnrollmentDocument.objects.create(
            enrollment=self.enrollment,
            name="DNI",
            file="enrollments/documents/dni.pdf",
            is_verified=True,
        )

        self.assertTrue(document.is_verified)


# ============================================================
# TESTS DE RELACIONES INVERSAS
# ============================================================

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