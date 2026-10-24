from datetime import datetime, timezone

from core.redis import redis_client

ONLINE_TIMEOUT = 60


def mark_user_online(user_id):
    key = f"academyhub:user:{user_id}:online"
    redis_client.set(key, "1", ex=ONLINE_TIMEOUT)


def is_user_online(user_id):
    key = f"academyhub:user:{user_id}:online"
    return redis_client.exists(key) == 1


def update_last_seen(user_id):
    key = f"academyhub:user:{user_id}:last_seen"
    redis_client.set(key, datetime.now(timezone.utc).isoformat())


def get_last_seen(user_id):
    key = f"academyhub:user:{user_id}:last_seen"
    return redis_client.get(key)
