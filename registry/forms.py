from django.forms import ModelForm

from .models.user_models import Patient
from .models.data_models import Hospital

# Create your models here.

class PatientRegisterForm(ModelForm):

    class Meta:
        model = Patient
        fields = ('first_name', 'middle_initial', 'last_name', 'date_of_birth', 'gender',
                  'email', 'password', 'height', 'weight', 'blood_type',
                  'insurance', 'pref_hospital', 'security_answer')

class HospitalRegisterForm(ModelForm):

    class Meta:
            model = Hospital
            fields = ('name', 'address', 'state', 'zipcode', 'identifiers')