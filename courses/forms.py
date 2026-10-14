from django import forms

from .models import Category, Convocatoria, Course, CourseImage


class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = [
            "academy",
            "category",
            "teacher",
            "title",
            "description",
            "objectives",
            "competences",
            "requirements",
            "level",
            "modality",
            "enrollment_mode",
            "requires_level_test",
            "is_negotiable",
            "duration_hours",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["academy"].queryset = user.academies.filter(is_active=True)
            self.fields["teacher"].queryset = self.fields["teacher"].queryset.filter(
                academy__owner=user, is_active=True
            )


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ["name", 
                "description",
                "icon"
        ]


class ConvocatoriaForm(forms.ModelForm):

    class Meta:
        model = Convocatoria
        fields = [
            "name",
            "start_date",
            "enrollment_deadline",
            "schedule",
            "modality",
            "location",
            "price",
            "deposit",
            "total_places",
            "is_active",
        ]


class CourseImageForm(forms.ModelForm):

    class Meta:
        model = CourseImage
        fields = ["image",
                "alt_text",
                "is_primary",
                "position"
        ]
