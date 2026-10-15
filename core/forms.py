from django import forms
from django.core.exceptions import ValidationError

from .models import ContactMessage


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput)
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data:
            return data
        if isinstance(data, (list, tuple)):
            if len(data) > 8:
                raise ValidationError("Se permiten un maximo de 8 imagenes.")
            result = []
            for file in data:
                cleaned = super().clean(file, initial)
                result.append(cleaned)
            return result
        return super().clean(data, initial)


def validate_image_size(file):
    if file.size > 5 * 1024 * 1024:
        raise ValidationError("El tamano maximo permitido es 5 MB.")
    return file


def validate_image_count(files):
    if len(files) > 8:
        raise ValidationError("Se permiten un maximo de 8 imagenes.")
    return files


class ContactMessageForm(forms.ModelForm):

    class Meta:
        model = ContactMessage
        fields = [
            "name",
            "email",
            "subject",
            "message",
        ]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }
