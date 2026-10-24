from django.contrib.auth import get_user_model
from core.test_base import VerboseTestCase
from django.urls import reverse

from notifications.models import Notification

User = get_user_model()


class NotificationTests(VerboseTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
        )
        self.notification = Notification.objects.create(
            user=self.user, title="Hola", message="Mensaje"
        )

    def test_user_sees_only_own_notifications(self):
        other = User.objects.create_user(
            username="carlos",
            email="carlos@example.com",
            password="TestPassword123!",
        )
        Notification.objects.create(user=other, title="Otro", message="...")

        self.client.force_login(self.user)
        response = self.client.get(reverse("notifications:list"))
        self.assertContains(response, "Hola")
        self.assertNotContains(response, "Otro")

    def test_mark_as_read(self):
        self.client.force_login(self.user)
        self.client.get(
            reverse("notifications:mark_as_read", kwargs={"pk": self.notification.pk})
        )
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)


    def test_notifications_filter_by_type(self):
        self.client.force_login(self.user)
        Notification.objects.create(
            user=self.user, title="NotifAviso", message="...", type="warning",
        )
        Notification.objects.create(
            user=self.user, title="NotifInfo", message="...", type="info",
        )
        response = self.client.get(
            reverse("notifications:list"),
            {"type": "warning"},
        )
        self.assertContains(response, "NotifAviso")
        self.assertNotContains(response, "NotifInfo")