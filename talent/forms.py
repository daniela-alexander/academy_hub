from django import forms

from .models import Competence, PassportEntry, TalentPassport


class CompetenceForm(forms.ModelForm):
    class Meta:
        model = Competence
        fields = ["name", "description", "category", "is_active"]


class PassportEntryForm(forms.ModelForm):
    class Meta:
        model = PassportEntry
        fields = ["competence", "level", "evidence"]


class TalentPassportForm(forms.ModelForm):
    class Meta:
        model = TalentPassport
        fields = ["headline", "summary"]
