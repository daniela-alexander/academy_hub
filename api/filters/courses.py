import django_filters

from courses.models import Course


class CourseFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name="convocatorias__price",
        lookup_expr="gte",
    )
    max_price = django_filters.NumberFilter(
        field_name="convocatorias__price",
        lookup_expr="lte",
    )

    class Meta:
        model = Course
        fields = [
            "category",
            "academy",
            "level",
            "modality",
            "status",
            "enrollment_mode",
            "is_negotiable",
            "requires_level_test",
        ]
