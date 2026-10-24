import django_filters

from payments.models import Payment


class PaymentFilter(django_filters.FilterSet):
    class Meta:
        model = Payment
        fields = ["status", "enrollment"]
