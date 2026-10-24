from rest_framework import serializers

from evaluations.models import Evaluation


class EvaluationSerializer(serializers.ModelSerializer):
    kind_display = serializers.CharField(source="get_kind_display", read_only=True)

    class Meta:
        model = Evaluation
        fields = [
            "id",
            "enrollment",
            "kind",
            "kind_display",
            "score",
            "feedback",
            "evaluated_by",
            "evaluated_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "evaluated_by",
            "evaluated_at",
            "created_at",
        ]
