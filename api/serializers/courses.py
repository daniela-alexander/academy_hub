from rest_framework import serializers

from courses.models import (
    Category,
    Convocatoria,
    Course,
    CourseFavorite,
    CourseImage,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "icon", "is_active"]
        read_only_fields = ["id", "slug"]


class CourseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseImage
        fields = ["id", "image", "alt_text", "is_primary", "position"]
        read_only_fields = ["id"]


class ConvocatoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Convocatoria
        fields = [
            "id",
            "course",
            "name",
            "start_date",
            "end_date",
            "enrollment_deadline",
            "schedule",
            "modality",
            "location",
            "price",
            "deposit",
            "total_places",
            "reserved_places",
            "enrolled_places",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reserved_places",
            "enrolled_places",
            "created_at",
            "updated_at",
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor que 0.")
        return value


class CourseSerializer(serializers.ModelSerializer):
    academy_name = serializers.CharField(source="academy.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    teacher_name = serializers.StringRelatedField(source="teacher", read_only=True)
    level_display = serializers.CharField(source="get_level_display", read_only=True)
    modality_display = serializers.CharField(source="get_modality_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    images = CourseImageSerializer(many=True, read_only=True)
    favorite_count = serializers.IntegerField(read_only=True)
    reviews_avg = serializers.FloatField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "academy",
            "academy_name",
            "category",
            "category_name",
            "teacher",
            "teacher_name",
            "title",
            "slug",
            "description",
            "objectives",
            "competences",
            "requirements",
            "level",
            "level_display",
            "modality",
            "modality_display",
            "status",
            "status_display",
            "enrollment_mode",
            "requires_level_test",
            "is_negotiable",
            "duration_hours",
            "views_count",
            "favorite_count",
            "reviews_avg",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "status",
            "views_count",
            "created_at",
            "updated_at",
        ]


class CourseFavoriteSerializer(serializers.ModelSerializer):
    course_detail = CourseSerializer(source="course", read_only=True)

    class Meta:
        model = CourseFavorite
        fields = ["id", "course", "course_detail", "created_at"]
        read_only_fields = ["id", "created_at"]
