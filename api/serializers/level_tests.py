from rest_framework import serializers

from level_tests.models import LevelTest, LevelTestAttempt, LevelTestQuestion


class LevelTestQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelTestQuestion
        fields = [
            "id",
            "question",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
        ]
        read_only_fields = fields


class LevelTestSerializer(serializers.ModelSerializer):
    questions = LevelTestQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = LevelTest
        fields = [
            "id",
            "course",
            "title",
            "description",
            "passing_score",
            "is_active",
            "questions",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class LevelTestAttemptSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = LevelTestAttempt
        fields = [
            "id",
            "student",
            "student_username",
            "level_test",
            "score",
            "passed",
            "started_at",
            "finished_at",
        ]
        read_only_fields = ["id", "student", "started_at"]
