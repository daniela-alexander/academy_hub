from rest_framework import serializers

from reviews.models import AcademyReview, CourseReview


class CourseReviewSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = CourseReview
        fields = [
            "id",
            "student",
            "student_username",
            "course",
            "course_title",
            "rating",
            "comment",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "student", "created_at", "updated_at"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La puntuación debe estar entre 1 y 5.")
        return value


class AcademyReviewSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)
    academy_name = serializers.CharField(source="academy.name", read_only=True)

    class Meta:
        model = AcademyReview
        fields = [
            "id",
            "student",
            "student_username",
            "academy",
            "academy_name",
            "rating",
            "comment",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "student", "created_at", "updated_at"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La puntuación debe estar entre 1 y 5.")
        return value
