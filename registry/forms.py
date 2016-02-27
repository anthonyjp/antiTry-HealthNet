from django.forms import ModelForm, CharField, PasswordInput, EmailField

from .models.user_models import Patient
from .models.data_models import Hospital

# Create your models here.

class PatientRegisterForm(ModelForm):
    first_name = CharField(max_length=25)
    last_name = CharField(max_length=30)
    password = CharField(max_length=40, widget=PasswordInput)
    email = EmailField(max_length=256)

    class Meta:
        model = Patient
        fields = ('first_name', 'middle_initial', 'last_name', 'date_of_birth', 'gender',
                  'email', 'password', 'height', 'weight', 'blood_type',
                  'insurance', 'pref_hospital', 'security_question', 'security_answer')
        widgets = {
            'password': PasswordInput
        }

class HospitalRegisterForm(ModelForm):

    class Meta:
            model = Hospital
            fields = ('name', 'address', 'state', 'zipcode', 'identifiers')