from django.core.cache import cache
from django.db.models import Count

from academies.models import Academy

POPULAR_ACADEMIES_KEY = "home:popular_academies"
POPULAR_ACADEMIES_TIMEOUT = 60


def get_popular_academies():
    """
    Devuelve las academias más populares cacheadas durante 60 segundos.
    Guardamos solo IDs y recuperamos objetos frescos de PostgreSQL.
    """
    academy_ids = cache.get(POPULAR_ACADEMIES_KEY)

    if academy_ids is None:
        academy_ids = list(
            Academy.objects
            .filter(is_active=True)
            .annotate(favorite_count=Count("favorites"))
            .order_by("-favorite_count", "-views_count")
            .values_list("id", flat=True)[:10]
        )
        cache.set(
            POPULAR_ACADEMIES_KEY,
            academy_ids,
            timeout=POPULAR_ACADEMIES_TIMEOUT,
        )

    if not academy_ids:
        return []

    academies = (
        Academy.objects
        .filter(id__in=academy_ids)
        .select_related("owner")
        .prefetch_related("courses")
    )

    order = {academy_id: i for i, academy_id in enumerate(academy_ids)}
    return sorted(academies, key=lambda a: order[a.id])


def invalidate_popular_academies():
    """
    Elimina el cache de academias populares.
    Se llama cada vez que cambia un favorito de academia.
    """
    cache.delete(POPULAR_ACADEMIES_KEY)