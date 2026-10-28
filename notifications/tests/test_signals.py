from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from academies.models import Academy
from chat.services import create_direct_conversation, send_message
from courses.models import Category, Convocatoria, Course
from enrollments.models import Enrollment
from notifications.models import Notification

User = get_user_model()


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class MessageSignalTests(TestCase):

    def setUp(self):
        self.student = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.teacher = User.objects.create_user(
            username="profesor",
            email="profesor@example.com",
            password="TestPassword123!",
            is_academy=True,
        )
        self.conv = create_direct_conversation(self.student, self.teacher)

    def test_new_message_creates_notification(self):
        send_message(self.student, self.conv.pk, "Hola profe")
        self.assertTrue(
            Notification.objects.filter(
                user=self.teacher,
                type=Notification.Type.NEW_MESSAGE,
            ).exists()
        )


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class EnrollmentSignalTests(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="academia",
            email="academia@example.com",
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
            status="published",
        )
        self.convocatoria = Convocatoria.objects.create(
            course=self.course,
            start_date="2026-07-01",
            end_date="2026-09-30",
            price=Decimal("480.00"),
            total_places=15,
        )

    def test_new_enrollment_creates_notification_for_academy(self):
        Enrollment.objects.create(
            student=self.student,
            convocatoria=self.convocatoria,
        )
        self.assertTrue(
            Notification.objects.filter(
                user=self.owner,
                type=Notification.Type.ENROLLMENT_RECEIVED,
            ).exists()
        )