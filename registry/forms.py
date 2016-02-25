from .models import Patient
from  django import forms
# Create your models here.

class PatientRegisterForm(forms.ModelForm):

    class Meta:
        model = Patient
        fields = ('firstName', 'middleInitial', 'lastName', 'dateOfBirth', 'gender',
                  'email', 'password', 'height', 'weight', 'bloodType',
                  'insurance', 'prefHospital', 'securityAnswer')