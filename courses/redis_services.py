from core.redis import redis_client


def increment_course_views(course_id):
    key = f"academyhub:course:{course_id}:views"
    return redis_client.incr(key)


def get_course_views(course_id):
    key = f"academyhub:course:{course_id}:views"
    value = redis_client.get(key)
    return int(value) if value else 0


def increment_academy_views(academy_id):
    key = f"academyhub:academy:{academy_id}:views"
    return redis_client.incr(key)


def get_academy_views(academy_id):
    key = f"academyhub:academy:{academy_id}:views"
    value = redis_client.get(key)
    return int(value) if value else 0
