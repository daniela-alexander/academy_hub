from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters.enrollments import EnrollmentFilter
from api.permissions import IsStudentOwnerOrReadOnly
from api.serializers.enrollments import EnrollmentSerializer
from enrollments.models import Enrollment
from enrollments.services import reserve_place


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, IsStudentOwnerOrReadOnly]
    filterset_class = EnrollmentFilter

    def get_queryset(self):
        return (
            Enrollment.objects
            .select_related("student", "convocatoria", "convocatoria__course")
            .prefetch_related("answers", "documents")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=False, methods=["get"])
    def mine(self, request):
        queryset = self.get_queryset().filter(student=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=["get"])
    def academy(self, request):
        queryset = self.get_queryset().filter(
            convocatoria__course__academy__owner=request.user
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        enrollment = self.get_object()

        if enrollment.convocatoria.course.academy.owner != request.user:
            return Response(
                {"detail": "No tienes permiso."},
                status=403,
            )

        enrollment.status = "approved"
        enrollment.save(update_fields=["status"])
        return Response(self.get_serializer(enrollment).data)

    @action(detail=True, methods=["post"])
    def enroll(self, request, pk=None):
        enrollment = self.get_object()

        if enrollment.convocatoria.course.academy.owner != request.user:
            return Response(
                {"detail": "No tienes permiso."},
                status=403,
            )

        enrollment.status = "enrolled"
        enrollment.save(update_fields=["status"])
        return Response(self.get_serializer(enrollment).data)


class ConvocatoriaReserveViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def reserve(self, request, pk=None):
        try:
            enrollment = reserve_place(request.user, pk)
            return Response(
                EnrollmentSerializer(enrollment).data,
                status=201,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)
