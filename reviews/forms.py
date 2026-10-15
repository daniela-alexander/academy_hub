from django import forms

from .models import AcademyReview, CourseReview


class CourseReviewForm(forms.ModelForm):
    class Meta:
        model = CourseReview
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "comment": forms.Textarea(attrs={"rows": 4}),
        }


class AcademyReviewForm(forms.ModelForm):
    class Meta:
        model = AcademyReview
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "comment": forms.Textarea(attrs={"rows": 4}),
        }
