from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from notifications.models import Notification
from notifications.tasks import (
    create_notification_async,
    send_notification_email_async,
)

User = get_user_model()


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class NotificationTaskTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
        )

    def test_create_notification_async(self):
        create_notification_async.delay(
            user_id=self.user.pk,
            notification_type=Notification.Type.INFO,
            title="Hola",
            message="Mensaje de prueba",
            url="/",
        )
        self.assertEqual(
            Notification.objects.filter(user=self.user).count(),
            1,
        )

    def test_send_email_async(self):
        result = send_notification_email_async.delay(
            user_id=self.user.pk,
            subject="Test",
            body="Cuerpo del email",
        )
        # En eager mode, result.result puede ser None hasta que se resuelva.
        # Usamos get() para forzarlo.
        self.assertEqual(
            result.get(),
            f"email_sent_for_user_{self.user.pk}",
        )