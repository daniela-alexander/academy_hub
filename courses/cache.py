from django.core.cache import cache
from django.db.models import Count

from courses.models import Course, CourseStatus

POPULAR_COURSES_KEY = "home:popular_courses"
POPULAR_COURSES_TIMEOUT = 60


def get_popular_courses():
    course_ids = cache.get(POPULAR_COURSES_KEY)

    if course_ids is None:
        course_ids = list(
            Course.objects
            .filter(status=CourseStatus.PUBLISHED)
            .annotate(favorite_count=Count("favorites"))
            .order_by("-favorite_count", "-views_count")
            .values_list("id", flat=True)[:10]
        )
        cache.set(
            POPULAR_COURSES_KEY,
            course_ids,
            timeout=POPULAR_COURSES_TIMEOUT,
        )

    if not course_ids:
        return []

    courses = (
        Course.objects
        .filter(id__in=course_ids)
        .select_related("academy", "category")
        .prefetch_related("images")
    )

    order = {course_id: i for i, course_id in enumerate(course_ids)}
    return sorted(courses, key=lambda c: order[c.id])

def invalidate_popular_courses():
    cache.delete(POPULAR_COURSES_KEY)
