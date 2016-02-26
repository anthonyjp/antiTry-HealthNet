from django.forms import ModelForm

from .models.user_models import Patient

# Create your models here.

class PatientRegisterForm(ModelForm):

    class Meta:
        model = Patient
        fields = ('firstName', 'middleInitial', 'lastName', 'dateOfBirth', 'gender',
                  'email', 'password', 'height', 'weight', 'bloodType',
                  'insurance', 'prefHospital', 'securityAnswer')