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
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()

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
            "location_name",
            "latitude",
            "longitude",
            "distance_km",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "slug",
            "views_count",
            "is_verified",
            "location_name",
            "latitude",
            "longitude",
            "distance_km",
            "created_at",
            "updated_at",
        ]

    def get_latitude(self, obj) -> float | None:
        return obj.location.y if obj.location else None

    def get_longitude(self, obj) -> float | None:
        return obj.location.x if obj.location else None

    def get_distance_km(self, obj) -> float | None:
        if hasattr(obj, "distance") and obj.distance is not None:
            return round(obj.distance.km, 2)
        return None
