import django_filters

from academies.models import Academy


class AcademyFilter(django_filters.FilterSet):
    class Meta:
        model = Academy
        fields = ["city", "is_verified", "is_active"]
