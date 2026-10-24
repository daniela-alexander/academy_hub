from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.permissions import IsStudentOwnerOrReadOnly
from api.serializers.reviews import AcademyReviewSerializer, CourseReviewSerializer
from reviews.models import AcademyReview, CourseReview


class CourseReviewViewSet(viewsets.ModelViewSet):
    serializer_class = CourseReviewSerializer
    permission_classes = [IsStudentOwnerOrReadOnly]
    filterset_fields = ["course", "rating", "is_published"]

    def get_queryset(self):
        return (
            CourseReview.objects
            .filter(is_published=True)
            .select_related("student", "course")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class AcademyReviewViewSet(viewsets.ModelViewSet):
    serializer_class = AcademyReviewSerializer
    permission_classes = [IsStudentOwnerOrReadOnly]
    filterset_fields = ["academy", "rating", "is_published"]

    def get_queryset(self):
        return (
            AcademyReview.objects
            .filter(is_published=True)
            .select_related("student", "academy")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class MyReviewViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            CourseReview.objects
            .filter(student=self.request.user)
            .select_related("course")
            .order_by("-created_at")
        )
