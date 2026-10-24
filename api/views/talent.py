from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import IsStaffOrReadOnly
from api.serializers.talent import (
    CompetenceSerializer,
    PassportEntrySerializer,
    TalentPassportSerializer,
)
from talent.models import Competence, PassportEntry, TalentPassport


class CompetenceViewSet(viewsets.ModelViewSet):
    serializer_class = CompetenceSerializer
    permission_classes = [IsStaffOrReadOnly]
    search_fields = ["name", "description"]

    def get_queryset(self):
        return Competence.objects.filter(is_active=True).order_by("name")


class TalentPassportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TalentPassportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TalentPassport.objects.filter(student=self.request.user)

    @action(detail=False, methods=["get"])
    def mine(self, request):
        passport, _ = TalentPassport.objects.get_or_create(student=request.user)
        return Response(TalentPassportSerializer(passport).data)


class PassportEntryViewSet(viewsets.ModelViewSet):
    serializer_class = PassportEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PassportEntry.objects.filter(
            passport__student=self.request.user
        ).select_related("competence").order_by("-obtained_at")
