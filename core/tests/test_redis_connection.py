from unittest.mock import patch

from django.test import TestCase


class RedisConnectionTests(TestCase):

    def test_redis_client_is_configured(self):
        from core.redis import redis_client

        self.assertIsNotNone(redis_client)

    def test_redis_client_has_decode_responses(self):
        from core.redis import redis_client

        # decode_responses=True significa que los valores llegan como str
        self.assertTrue(redis_client.connection_pool.connection_kwargs.get("decode_responses", False))

    @patch("redis.Redis.ping")
    def test_redis_ping(self, mock_ping):
        mock_ping.return_value = True

        from core.redis import redis_client

        self.assertTrue(redis_client.ping())