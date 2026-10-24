from django.db import transaction

from courses.models import Course, CourseStatus


@transaction.atomic
def archive_course(course_id, user):
    course = (
        Course.objects
        .select_for_update()
        .get(pk=course_id)
    )

    if course.academy.owner != user:
        raise ValueError("No tienes permiso para archivar este curso.")

    course.status = CourseStatus.ARCHIVED
    course.save(update_fields=["status"])
    return course
