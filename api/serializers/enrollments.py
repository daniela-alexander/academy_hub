from rest_framework import serializers

from enrollments.models import (
    Enrollment,
    EnrollmentAnswer,
    EnrollmentDocument,
    WaitlistEntry,
)


class EnrollmentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrollmentAnswer
        fields = ["id", "question_key", "question_text", "answer_text", "created_at"]
        read_only_fields = ["id", "created_at"]


class EnrollmentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrollmentDocument
        fields = ["id", "name", "file", "is_verified", "uploaded_at"]
        read_only_fields = ["id", "is_verified", "uploaded_at"]


class EnrollmentSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)
    course_title = serializers.CharField(
        source="convocatoria.course.title", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_status_display = serializers.CharField(
        source="get_payment_status_display", read_only=True
    )
    answers = EnrollmentAnswerSerializer(many=True, read_only=True)
    documents = EnrollmentDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "student_username",
            "convocatoria",
            "course_title",
            "status",
            "status_display",
            "payment_status",
            "payment_status_display",
            "amount_paid",
            "discount_amount",
            "reservation_expires_at",
            "enrolled_at",
            "completed_at",
            "notes",
            "answers",
            "documents",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student",
            "payment_status",
            "amount_paid",
            "discount_amount",
            "enrolled_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]


class WaitlistEntrySerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = WaitlistEntry
        fields = [
            "id",
            "student",
            "student_username",
            "convocatoria",
            "position",
            "is_notified",
            "notified_at",
            "converted_to_enrollment",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "student",
            "position",
            "notified_at",
            "converted_to_enrollment",
            "created_at",
        ]
