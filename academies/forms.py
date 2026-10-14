from django import forms
from .models import Academy, Teacher

class AcademyForm(forms.ModelForm):
    class Meta:
        model = Academy
        fields = [
            "name",
            "description",
            "city",
            "address",
            "website",
            "phone",
            "email",
            "logo",
]
        
class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "specialty",
            "bio",
            "photo",
]
        
    def __init__(self, *args, **kwargs):
        self.academy = kwargs.pop("academy", None)
        super().__init__(*args, **kwargs)
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.academy and not instance.academy_id:
            instance.academy = self.academy
        if commit:
            instance.save()
        return instance