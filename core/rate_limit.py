import logging

from core.redis import redis_client

logger = logging.getLogger(__name__)


def check_rate_limit(key, limit, window):
    """
    Devuelve True si la petición está permitida.
    Si Redis falla, devuelve True (fail-open) para no bloquear al usuario.
    """
    try:
        current = redis_client.incr(key)

        if current == 1:
            redis_client.expire(key, window)

        return current <= limit

    except Exception:
        logger.exception("Rate limit failed for key=%s", key)
        # Fail-open: si Redis falla, permitimos la acción
        return True