from core.geo_services import parse_geo_params


class DistanceOrderingMixin:
    """
    OrderingFilter aplica el orden por defecto de la vista, que anularía el orden
    por distancia. Se conserva salvo que el cliente pida ?ordering= explícitamente.
    """

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        params = self.request.query_params
        if parse_geo_params(params) and "ordering" not in params:
            return queryset.order_by("distance")
        return queryset
