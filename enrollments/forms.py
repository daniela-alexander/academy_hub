from django import forms

from .models import Enrollment, EnrollmentAnswer, EnrollmentDocument


class EnrollmentForm(forms.ModelForm):

    class Meta:
        model = Enrollment
        fields = []

    def __init__(self, *args, **kwargs):
        self.student = kwargs.pop("student", None)
        self.convocatoria = kwargs.pop("convocatoria", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.student and not instance.student_id:
            instance.student = self.student
        if self.convocatoria and not instance.convocatoria_id:
            instance.convocatoria = self.convocatoria
        if commit:
            instance.save()
        return instance


class EnrollmentAnswerForm(forms.ModelForm):

    class Meta:
        model = EnrollmentAnswer
        fields = ["question_key",
                "question_text",
                "answer_text"
            ]


class EnrollmentDocumentForm(forms.ModelForm):

    class Meta:
        model = EnrollmentDocument
        fields = ["name",
                "file"
        ]
