from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers.evaluations import EvaluationSerializer
from evaluations.models import Evaluation


class EvaluationViewSet(viewsets.ModelViewSet):
    serializer_class = EvaluationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_academy:
            return Evaluation.objects.filter(
                enrollment__convocatoria__course__academy__owner=self.request.user
            ).order_by("-created_at")
        return Evaluation.objects.filter(enrollment__student=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(evaluated_by=self.request.user)

    @action(detail=False, methods=["get"])
    def mine(self, request):
        queryset = Evaluation.objects.filter(enrollment__student=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=["get"])
    def academy(self, request):
        queryset = Evaluation.objects.filter(
            enrollment__convocatoria__course__academy__owner=request.user
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response(self.get_serializer(queryset, many=True).data)
