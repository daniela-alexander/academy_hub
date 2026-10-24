from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers.level_tests import (
    LevelTestAttemptSerializer,
    LevelTestSerializer,
)
from level_tests.models import LevelTest, LevelTestAttempt


class LevelTestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LevelTestSerializer
    filterset_fields = ["course", "is_active"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        return LevelTest.objects.filter(is_active=True).select_related("course")

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def attempt(self, request, pk=None):
        level_test = self.get_object()

        score = request.data.get("score", 0)
        passed = score >= level_test.passing_score

        attempt = LevelTestAttempt.objects.create(
            student=request.user,
            level_test=level_test,
            score=score,
            passed=passed,
            finished_at=timezone.now(),
        )

        return Response(LevelTestAttemptSerializer(attempt).data, status=201)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def attempts_mine(self, request, pk=None):
        level_test = self.get_object()
        attempts = LevelTestAttempt.objects.filter(
            student=request.user,
            level_test=level_test,
        ).order_by("-started_at")
        return Response(LevelTestAttemptSerializer(attempts, many=True).data)
