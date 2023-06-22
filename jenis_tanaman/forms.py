from django import forms
from django.core.validators import FileExtensionValidator

from .models import JenisTanaman

class JenisTanamanForm(forms.ModelForm):
    class Meta:
        model = JenisTanaman
        fields = '__all__'
        widgets = {
            'model': forms.FileInput(attrs={'accept': '.tflite'}),
        }
        validators = {
            'model': [FileExtensionValidator(allowed_extensions=['tflite'])],
        }
