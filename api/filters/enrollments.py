import django_filters

from enrollments.models import Enrollment


class EnrollmentFilter(django_filters.FilterSet):
    class Meta:
        model = Enrollment
        fields = ["status", "payment_status", "convocatoria", "student"]
