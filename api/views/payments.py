from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers.payments import (
    DiscountSerializer,
    PaymentSerializer,
    ScholarshipSerializer,
)
from payments.models import Discount, Payment, Scholarship


class DiscountViewSet(viewsets.ModelViewSet):
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Discount.objects.all().order_by("-created_at")
        return Discount.objects.filter(is_active=True).order_by("-created_at")


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_academy:
            return Payment.objects.filter(
                enrollment__convocatoria__course__academy__owner=self.request.user
            ).order_by("-created_at")
        return Payment.objects.filter(enrollment__student=self.request.user).order_by("-created_at")

    @action(detail=False, methods=["get"])
    def mine(self, request):
        queryset = Payment.objects.filter(enrollment__student=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response(self.get_serializer(queryset, many=True).data)


class ScholarshipViewSet(viewsets.ModelViewSet):
    serializer_class = ScholarshipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_academy:
            return Scholarship.objects.filter(
                enrollment__convocatoria__course__academy__owner=self.request.user
            ).order_by("-created_at")
        return Scholarship.objects.filter(student=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        scholarship = self.get_object()
        if not request.user.is_academy:
            return Response({"detail": "Solo academias."}, status=403)
        scholarship.status = Scholarship.Status.APPROVED
        scholarship.save()
        return Response(self.get_serializer(scholarship).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        scholarship = self.get_object()
        if not request.user.is_academy:
            return Response({"detail": "Solo academias."}, status=403)
        scholarship.status = Scholarship.Status.REJECTED
        scholarship.save()
        return Response(self.get_serializer(scholarship).data)
