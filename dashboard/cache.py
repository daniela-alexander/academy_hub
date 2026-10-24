from django.core.cache import cache
from django.db.models import Avg, Sum

from courses.models import Convocatoria, Course
from enrollments.models import Enrollment
from payments.models import Payment
from reviews.models import CourseReview

STATS_KEY = "home:stats"
STATS_TIMEOUT = 300


def get_global_stats():
    """
    Devuelve las estadísticas globales cacheadas durante 300 segundos.
    """
    stats = cache.get(STATS_KEY)

    if stats is None:
        stats = {
            "total_courses": Course.objects.count(),
            "published_courses": Course.objects.filter(
                status="published"
            ).count(),
            "total_enrollments": Enrollment.objects.count(),
            "total_reviews": CourseReview.objects.count(),
            "avg_rating": float(
                CourseReview.objects.aggregate(avg=Avg("rating"))["avg"] or 0
            ),
            "total_revenue": float(
                Payment.objects.filter(status="paid").aggregate(
                    total=Sum("amount")
                )["total"] or 0
            ),
            "avg_price": float(
                Convocatoria.objects.filter(is_active=True).aggregate(
                    avg=Avg("price")
                )["avg"] or 0
            ),
        }
        cache.set(STATS_KEY, stats, timeout=STATS_TIMEOUT)

    return stats


def invalidate_global_stats():
    """
    Elimina el cache de estadísticas globales.
    Se llama cuando cambia algo relevante: nueva inscripción, nuevo pago,
    nueva reseña, nuevo curso publicado.
    """
    cache.delete(STATS_KEY)