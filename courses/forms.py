from django import forms

from .models import Category, Convocatoria, Course, CourseImage


from django import forms

from core.forms import MultipleFileField

from .models import Category, Convocatoria, Course


class CourseForm(forms.ModelForm):
    images = MultipleFileField(required=False)

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
                academy__owner=user,
                is_active=True,
            )

    def clean_images(self):
        images = self.cleaned_data.get("images") or []

        if len(images) > 8:
            raise forms.ValidationError(
                "Puedes subir como máximo 8 imágenes."
            )

        max_size = 5 * 1024 * 1024  # 5 MB
        for image in images:
            if image.size > max_size:
                raise forms.ValidationError(
                    "Cada imagen no puede superar los 5 MB."
                )

        return images



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
