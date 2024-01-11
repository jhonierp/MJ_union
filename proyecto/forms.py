from django import forms
from .models import PersonasNaturales

class PNatuForm(forms.ModelForm):
    class Meta:
        model=PersonasNaturales
        fields='__all__'
        
        
# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username','email', 'rol']

class TrabajadorRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'password']
        
        
        
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)