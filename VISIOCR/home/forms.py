# forms.py
from django import forms
from .models import VisitorPass

class VisitorPassForm(forms.ModelForm):
    class Meta:
        model = VisitorPass
        fields = ['name', 'mobile_number', 'date_of_visiting', 'duration_of_visiting', 'aadhaar_image']
        widgets = {
            'date_of_visiting': forms.SelectDateWidget,
        }
    aadhaar_image = forms.ImageField(required=True, label='Select Aadhaar Image')
