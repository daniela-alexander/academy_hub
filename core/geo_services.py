from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from academies.models import Academy
from courses.models import Course, CourseStatus


def _build_point(latitude, longitude):
    """Construye un Point a partir de latitud y longitud."""
    return Point(float(longitude), float(latitude), srid=4326)


def get_academies_nearby(latitude, longitude, radius_km=15):
    """
    Devuelve las academias activas dentro de un radio en km.
    Ordena por distancia ascendente.
    """
    user_location = _build_point(latitude, longitude)


    return (
        Academy.objects
        .filter(is_active=True)
        .filter(location__isnull=False)
        .filter(
            location__distance_lte=(user_location, D(km=radius_km))
        )
        .annotate(distance=Distance("location", user_location))
        .order_by("distance")
    )


def get_courses_nearby(latitude, longitude, radius_km=15):
    """
    Devuelve los cursos publicados cuya academia está dentro de un radio en km.
    Ordena por distancia ascendente.
    """
    user_location = _build_point(latitude, longitude)

    
    return (
        Course.objects
        .filter(status=CourseStatus.PUBLISHED)
        .filter(academy__location__isnull=False)
        .filter(
            academy__location__distance_lte=(user_location, D(km=radius_km))
        )
        .select_related("academy", "category", "teacher")
        .prefetch_related("images")
        .annotate(distance=Distance("academy__location", user_location))
        .order_by("distance")
)