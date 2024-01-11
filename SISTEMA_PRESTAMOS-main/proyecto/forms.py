from django import forms
from .models import PersonasNaturales

class PNatuForm(forms.ModelForm):
    class Meta:
        model=PersonasNaturales
        fields='__all__'