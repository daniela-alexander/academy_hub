from rest_framework import serializers

from talent.models import Competence, PassportEntry, TalentPassport


class CompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competence
        fields = ["id", "name", "description", "category", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class PassportEntrySerializer(serializers.ModelSerializer):
    competence_name = serializers.CharField(source="competence.name", read_only=True)

    class Meta:
        model = PassportEntry
        fields = [
            "id",
            "passport",
            "competence",
            "competence_name",
            "level",
            "evidence",
            "obtained_at",
        ]
        read_only_fields = ["id", "obtained_at"]

    def validate_level(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("El nivel debe estar entre 1 y 5.")
        return value


class TalentPassportSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)
    entries = PassportEntrySerializer(many=True, read_only=True)

    class Meta:
        model = TalentPassport
        fields = [
            "id",
            "student",
            "student_username",
            "headline",
            "summary",
            "entries",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "student", "created_at", "updated_at"]
