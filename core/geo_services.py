import math

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from academies.models import Academy
from courses.models import Course, CourseStatus

DEFAULT_RADIUS_KM = 20


def _build_point(latitude, longitude):
    """Construye un Point a partir de latitud y longitud."""
    return Point(float(longitude), float(latitude), srid=4326)


def parse_geo_params(params):
    """
    Lee lat, lng y distance_km de los parámetros de una petición.
    Devuelve (latitud, longitud, radio_km), o None si faltan o no son válidos.
    """
    raw_latitude = params.get("lat")
    raw_longitude = params.get("lng")
    if not raw_latitude or not raw_longitude:
        return None

    try:
        latitude = float(raw_latitude)
        longitude = float(raw_longitude)
        radius_km = float(params.get("distance_km") or DEFAULT_RADIUS_KM)
    except (TypeError, ValueError):
        return None

    if not all(math.isfinite(value) for value in (latitude, longitude, radius_km)):
        return None
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180 and radius_km > 0):
        return None

    return latitude, longitude, radius_km


def filter_within_radius(queryset, field, latitude, longitude, radius_km):
    """
    Filtra por un campo geográfico dentro de un radio en km.
    Anota la distancia y ordena de menor a mayor.
    """
    user_location = _build_point(latitude, longitude)

    return (
        queryset
        .filter(**{f"{field}__isnull": False})
        .filter(**{f"{field}__distance_lte": (user_location, D(km=radius_km))})
        .annotate(distance=Distance(field, user_location))
        .order_by("distance")
    )


def get_academies_nearby(latitude, longitude, radius_km=15):
    """
    Devuelve las academias activas dentro de un radio en km.
    Ordena por distancia ascendente.
    """
    return filter_within_radius(
        Academy.objects.filter(is_active=True),
        "location",
        latitude,
        longitude,
        radius_km,
    )


def get_courses_nearby(latitude, longitude, radius_km=15):
    """
    Devuelve los cursos publicados cuya academia está dentro de un radio en km.
    Ordena por distancia ascendente.
    """
    return filter_within_radius(
        Course.objects
        .filter(status=CourseStatus.PUBLISHED)
        .select_related("academy", "category", "teacher")
        .prefetch_related("images"),
        "academy__location",
        latitude,
        longitude,
        radius_km,
    )
