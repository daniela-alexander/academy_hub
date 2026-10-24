from django.db.models import Avg, Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from api.filters.courses import CourseFilter
from api.permissions import IsCourseAcademyOwnerOrReadOnly
from api.serializers.courses import (
    CategorySerializer,
    CourseFavoriteSerializer,
    CourseSerializer,
)
from courses.models import Category, Course, CourseFavorite
from courses.services import archive_course


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Category.objects.filter(is_active=True).order_by("name")


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsCourseAcademyOwnerOrReadOnly]
    filterset_class = CourseFilter
    search_fields = [
        "title",
        "description",
        "objectives",
        "competences",
        "academy__name",
        "category__name",
    ]
    ordering_fields = [
        "created_at",
        "views_count",
        "duration_hours",
        "favorite_count",
        "reviews_avg",
    ]
    ordering = ["-created_at"]
    lookup_field = "pk"

    def get_queryset(self):
        return (
            Course.objects
            .filter(status="published")
            .select_related("academy", "category", "teacher")
            .prefetch_related("images", "convocatorias")
            .annotate(
                favorite_count=Count("favorites", distinct=True),
                reviews_avg=Avg("reviews__rating"),
            )
        )

    def perform_create(self, serializer):
        if not self.request.user.is_academy:
            raise PermissionDenied(
                "Solo las academias pueden crear cursos."
            )

        academy = self.request.user.academies.first()
        if academy is None:
            raise PermissionDenied(
                "Necesitas crear una academia antes de publicar un curso."
            )

        serializer.save(academy=academy)

    def perform_destroy(self, instance):
        archive_course(instance.pk, self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def mine(self, request):
        queryset = (
            Course.objects
            .filter(academy__owner=request.user)
            .select_related("academy", "category", "teacher")
            .annotate(
                favorite_count=Count("favorites", distinct=True),
                reviews_avg=Avg("reviews__rating"),
            )
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=True, methods=["get"])
    def similar(self, request, pk=None):
        course = self.get_object()
        similar = self.get_queryset().filter(category=course.category).exclude(pk=course.pk)
        page = self.paginate_queryset(similar)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response(self.get_serializer(similar, many=True).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        course = self.get_object()

        if course.academy.owner == request.user:
            return Response(
                {"detail": "No puedes guardar tu propio curso."},
                status=400,
            )

        favorite, created = CourseFavorite.objects.get_or_create(
            user=request.user,
            course=course,
        )

        if created:
            return Response({"favorited": True}, status=201)

        favorite.delete()
        return Response({"favorited": False}, status=200)


class CourseFavoriteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseFavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            CourseFavorite.objects
            .filter(user=self.request.user)
            .select_related("course", "course__academy", "course__category")
            .prefetch_related("course__images")
        )
