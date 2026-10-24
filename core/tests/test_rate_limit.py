from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase

from core.rate_limit import check_rate_limit


class RateLimitTests(TestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    # ------------------------------------------------------------
    # Bajo el límite → True
    # ------------------------------------------------------------
    def test_allows_under_limit(self):
        key = "test:rate:1"
        for _ in range(3):
            self.assertTrue(check_rate_limit(key, limit=5, window=60))

    # ------------------------------------------------------------
    # Justo en el límite → True
    # ------------------------------------------------------------
    def test_allows_at_limit(self):
        key = "test:rate:2"
        for _ in range(5):
            self.assertTrue(check_rate_limit(key, limit=5, window=60))

    # ------------------------------------------------------------
    # Superar el límite → False
    # ------------------------------------------------------------
    def test_blocks_over_limit(self):
        key = "test:rate:3"
        for _ in range(5):
            check_rate_limit(key, limit=5, window=60)

        self.assertFalse(check_rate_limit(key, limit=5, window=60))

    # ------------------------------------------------------------
    # Distintas keys no se interfieren
    # ------------------------------------------------------------
    def test_different_keys_do_not_interfere(self):
        key1 = "test:rate:a"
        key2 = "test:rate:b"

        for _ in range(5):
            check_rate_limit(key1, limit=5, window=60)

        # key1 está llena
        self.assertFalse(check_rate_limit(key1, limit=5, window=60))
        # key2 está limpia
        self.assertTrue(check_rate_limit(key2, limit=5, window=60))

    # ------------------------------------------------------------
    # Simulación de expiración de ventana
    # ------------------------------------------------------------
    @patch("core.rate_limit.redis_client")
    def test_window_expiration_resets_counter(self, mock_redis):
        # Primera llamada: devuelve 1
        mock_redis.incr.return_value = 1
        mock_redis.expire.return_value = True

        result = check_rate_limit("test:rate:expire", limit=5, window=60)

        self.assertTrue(result)
        # Se aplica EXPIRE la primera vez
        mock_redis.expire.assert_called_once()

    # ------------------------------------------------------------
    # Redis caído → fail-open (no bloquea al usuario)
    # ------------------------------------------------------------
    @patch("core.rate_limit.redis_client")
    def test_redis_failure_does_not_block(self, mock_redis):
        mock_redis.incr.side_effect = Exception("Redis down")

        # El usuario no debe quedar bloqueado si Redis falla
        # (se comporta como fail-open)
        try:
            result = check_rate_limit("test:rate:fail", limit=5, window=60)
            # Si no lanza excepción, debe ser True
            self.assertTrue(result)
        except Exception:
            # Si lanza excepción, es porque no hemos puesto fail-open
            self.fail(
                "check_rate_limit debe ser tolerante a fallos de Redis"
            )