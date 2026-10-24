from django.contrib.auth import get_user_model
from core.test_base import VerboseTestCase
import time

from notifications.models import Notification

User = get_user_model()


class NotificationModelTests(VerboseTestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
        )

    def test_create_notification(self):
        notification = Notification.objects.create(
            user=self.user,
            title="Hola",
            message="Mensaje",
        )
        self.assertEqual(notification.title, "Hola")
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.type, Notification.Type.INFO)

    def test_string_representation(self):
        notification = Notification.objects.create(
            user=self.user,
            title="Hola",
            message="Mensaje",
        )
        self.assertIn("Hola", str(notification))
        self.assertIn(self.user.username, str(notification))

    def test_ordering_is_recent_first(self):
        n1 = Notification.objects.create(
            user=self.user,
            title="Primera",
            message="...",
        )
        time.sleep(0.01)
        n2 = Notification.objects.create(
            user=self.user,
            title="Segunda",
            message="...",
        )
        notifications = list(Notification.objects.all())
        self.assertEqual(notifications[0], n2)
        self.assertEqual(notifications[1], n1)