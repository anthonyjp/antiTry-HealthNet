from django.forms import forms, models, fields, widgets

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models.user_models import Patient
from .models.data_models import Hospital

from .utility.widgets import HeightField, WeightField
from .utility.options import BloodType

# Create your models here.

class PatientRegisterForm(models.ModelForm):
    first_name = fields.CharField(max_length=25)
    last_name = fields.CharField(max_length=30)
    password = fields.CharField(max_length=40, widget=widgets.PasswordInput)
    email = fields.EmailField(max_length=256)
    height = HeightField(required=True)
    weight = WeightField(required=True)

    def __init__(self, *args, **kwargs):
        super(PatientRegisterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'hn-form register'
        self.helper.form_method = 'POST'
        self.helper.form_action = 'new'

        self.helper.add_input(Submit('submit', 'Submit'))

        self.fields['pref_hospital'].required = False
        self.fields['middle_initial'].required = False
        self.fields['blood_type'].required = False
        self.fields['blood_type'].initial = BloodType.UNKNOWN
        self.fields['date_of_birth'].widget.attrs['datepicker'] = True

    class Meta:
        model = Patient
        fields = ('first_name', 'middle_initial', 'last_name', 'date_of_birth', 'gender',
                  'email', 'password', 'height', 'weight', 'blood_type',
                  'insurance', 'pref_hospital', 'security_question', 'security_answer')
        widgets = {
            'password': widgets.PasswordInput
        }


class HospitalRegisterForm(models.ModelForm):

    class Meta:
            model = Hospital
            fields = ('name', 'address', 'state', 'zipcode', 'identifiers')