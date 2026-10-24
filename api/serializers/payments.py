from rest_framework import serializers

from payments.models import Discount, Payment, Scholarship


class DiscountSerializer(serializers.ModelSerializer):
    discount_type_display = serializers.CharField(
        source="get_discount_type_display", read_only=True
    )

    class Meta:
        model = Discount
        fields = [
            "id",
            "code",
            "description",
            "discount_type",
            "discount_type_display",
            "value",
            "valid_from",
            "valid_until",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "enrollment",
            "amount",
            "status",
            "status_display",
            "discount",
            "reference",
            "paid_at",
            "created_at",
        ]
        read_only_fields = ["id", "paid_at", "created_at"]


class ScholarshipSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Scholarship
        fields = [
            "id",
            "student",
            "enrollment",
            "status",
            "status_display",
            "amount",
            "reason",
            "reviewed_by",
            "reviewed_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "student",
            "status",
            "reviewed_by",
            "reviewed_at",
            "created_at",
        ]
