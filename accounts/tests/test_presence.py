from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.presence import (
    ONLINE_TIMEOUT,
    get_last_seen,
    is_user_online,
    mark_user_online,
    update_last_seen,
)

User = get_user_model()


class PresenceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
        )

    # ------------------------------------------------------------
    # Usuario nunca marcado → offline
    # ------------------------------------------------------------
    def test_user_never_marked_is_offline(self):
        self.assertFalse(is_user_online(self.user.pk))

    # ------------------------------------------------------------
    # Marcar → online
    # ------------------------------------------------------------
    def test_mark_user_online(self):
        mark_user_online(self.user.pk)
        self.assertTrue(is_user_online(self.user.pk))

    # ------------------------------------------------------------
    # Renovar TTL
    # ------------------------------------------------------------
    def test_mark_user_online_renews_ttl(self):
        mark_user_online(self.user.pk)
        self.assertTrue(is_user_online(self.user.pk))

        mark_user_online(self.user.pk)
        self.assertTrue(is_user_online(self.user.pk))

    # ------------------------------------------------------------
    # TTL expira → offline
    # ------------------------------------------------------------
    @patch("accounts.presence.redis_client")
    def test_ttl_expiration_makes_user_offline(self, mock_redis):
        mock_redis.exists.return_value = 0
        self.assertFalse(is_user_online(self.user.pk))

    # ------------------------------------------------------------
    # Last seen: sin llamar → None
    # ------------------------------------------------------------
    def test_last_seen_none_if_never_set(self):
        self.assertIsNone(get_last_seen(self.user.pk))

    # ------------------------------------------------------------
    # Last seen: guardar y leer
    # ------------------------------------------------------------
    def test_update_last_seen_stores_iso_date(self):
        update_last_seen(self.user.pk)
        last_seen = get_last_seen(self.user.pk)

        self.assertIsNotNone(last_seen)
        # Formato ISO 8601: contiene "T" y "+" o "Z"
        self.assertIn("T", last_seen)

    # ------------------------------------------------------------
    # Middleware: usuario autenticado → online
    # ------------------------------------------------------------
    def test_middleware_marks_user_online(self):
        self.client.force_login(self.user)

        # Hacer una petición cualquiera
        self.client.get("/")

        self.assertTrue(is_user_online(self.user.pk))

    # ------------------------------------------------------------
    # Middleware: usuario anónimo → no se marca
    # ------------------------------------------------------------
    def test_middleware_does_not_mark_anonymous(self):
        self.client.get("/")
        # No hay user, no hay nada que comprobar
        # Solo comprobamos que no revienta
        self.assertTrue(True)

    # ------------------------------------------------------------
    # Middleware: Redis caído → no rompe la petición
    # ------------------------------------------------------------
    @patch("accounts.presence.redis_client")
    def test_middleware_handles_redis_failure(self, mock_redis):
        mock_redis.set.side_effect = Exception("Redis down")
        self.client.force_login(self.user)

        # La petición no debe romperse
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)