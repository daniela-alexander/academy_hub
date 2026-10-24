from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from academies.models import Academy, AcademyFavorite, Teacher
from api.filters.academies import AcademyFilter
from api.permissions import (
    IsAcademyOwnerOrReadOnly,
    IsTeacherAcademyOwnerOrReadOnly,
)
from api.serializers.academies import AcademySerializer, TeacherSerializer
from api.serializers.courses import CourseSerializer


class AcademyViewSet(viewsets.ModelViewSet):
    serializer_class = AcademySerializer
    permission_classes = [IsAcademyOwnerOrReadOnly]
    filterset_class = AcademyFilter
    search_fields = ["name", "description", "city"]
    ordering_fields = ["created_at", "name", "views_count"]
    ordering = ["-created_at"]
    lookup_field = "slug"

    def get_queryset(self):
        return (
            Academy.objects
            .filter(is_active=True)
            .select_related("owner")
            .annotate(
                teachers_count=Count("teachers", distinct=True),
                courses_count=Count("courses", distinct=True),
                favorite_count=Count("favorites", distinct=True),
            )
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def mine(self, request):
        queryset = self.get_queryset().filter(owner=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=True, methods=["get"])
    def teachers(self, request, slug=None):
        academy = self.get_object()
        teachers = academy.teachers.filter(is_active=True)
        return Response(TeacherSerializer(teachers, many=True).data)

    @action(detail=True, methods=["get"])
    def courses(self, request, slug=None):
        academy = self.get_object()
        courses = academy.courses.filter(status="published")
        page = self.paginate_queryset(courses)
        if page is not None:
            return self.get_paginated_response(
                CourseSerializer(page, many=True).data
            )
        return Response(CourseSerializer(courses, many=True).data)
    @extend_schema(
    summary="Alternar favorito de curso",
    responses={201: None, 200: None, 400: None},
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def favorite(self, request, slug=None):
        academy = self.get_object()

        if academy.owner == request.user:
            return Response(
                {"detail": "No puedes guardar tu propia academia."},
                status=400,
            )

        favorite, created = AcademyFavorite.objects.get_or_create(
            user=request.user,
            academy=academy,
        )

        if created:
            return Response({"favorited": True}, status=201)

        favorite.delete()
        return Response({"favorited": False}, status=200)


class TeacherViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherSerializer
    permission_classes = [IsTeacherAcademyOwnerOrReadOnly]

    def get_queryset(self):
        return Teacher.objects.select_related("academy").filter(is_active=True)
