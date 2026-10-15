from django import forms

from .models import LevelTest, LevelTestAttempt


class LevelTestForm(forms.ModelForm):
    class Meta:
        model = LevelTest
        fields = ["course", "title", "description", "passing_score", "is_active"]


class LevelTestAttemptForm(forms.ModelForm):
    class Meta:
        model = LevelTestAttempt
        fields = ["score", "passed"]
