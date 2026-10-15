from django import forms

from .models import Discount, Payment, Scholarship


class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = [
            "code",
            "description",
            "discount_type",
            "value",
            "valid_from",
            "valid_until",
            "is_active",
        ]


class ScholarshipForm(forms.ModelForm):
    class Meta:
        model = Scholarship
        fields = ["reason"]


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount", "discount", "reference"]
