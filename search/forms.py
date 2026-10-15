from django import forms


class CourseSearchForm(forms.Form):
    q = forms.CharField(required=False, label="Buscar")
    category = forms.IntegerField(required=False)
    level = forms.CharField(required=False)
    modality = forms.CharField(required=False)
    max_price = forms.DecimalField(required=False, min_value=0)
