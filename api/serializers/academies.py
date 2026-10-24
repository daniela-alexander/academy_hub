from rest_framework import serializers

from academies.models import Academy, Teacher


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = [
            "id",
            "academy",
            "first_name",
            "last_name",
            "email",
            "phone",
            "specialty",
            "bio",
            "photo",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AcademySerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    teachers_count = serializers.IntegerField(read_only=True)
    courses_count = serializers.IntegerField(read_only=True)
    favorite_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Academy
        fields = [
            "id",
            "owner",
            "name",
            "slug",
            "description",
            "city",
            "address",
            "website",
            "phone",
            "email",
            "logo",
            "is_verified",
            "is_active",
            "views_count",
            "teachers_count",
            "courses_count",
            "favorite_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "slug",
            "views_count",
            "is_verified",
            "created_at",
            "updated_at",
        ]
