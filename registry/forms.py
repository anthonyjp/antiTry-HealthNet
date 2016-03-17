from django.forms import forms, models, fields, widgets
from django import forms
from django.core.urlresolvers import reverse_lazy
from localflavor.us.forms import USPhoneNumberField

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

from .models.user_models import Patient, Prescription
from .models.data_models import Hospital
from .models.info_models import Appointment
from .models.message_models import Message,Inbox

from .utility.widgets import HeightField, WeightField, DateTimeMultiField
from .utility.options import BloodType, Relationship
from .utility.models import TimeRange

class PatientRegisterForm(models.ModelForm):
    model = Patient
    first_name = fields.CharField( max_length=25 )
    last_name = fields.CharField( max_length=30 )
    password = fields.CharField( max_length=40, widget=widgets.PasswordInput )
    email = fields.EmailField( max_length=256 )
    height = HeightField( required=True )
    weight = WeightField( required=True )
    contact_name = fields.CharField( max_length=60 )
    contact_relationship = fields.ChoiceField( choices=Relationship.choices( ), initial=Relationship.OTHER )
    contact_primary = USPhoneNumberField( required=True )
    contact_secondary = USPhoneNumberField( required=False )
    contact_email = fields.EmailField( required=True )

    def __init__(self, *args, **kwargs):
        super( PatientRegisterForm, self ).__init__( *args, **kwargs )
        self.helper = FormHelper( )
        self.helper.form_class = 'form-horizontal hn-form register'
        self.helper.form_method = 'POST'
        self.helper.form_action = 'register'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
            Fieldset( 'Patient Registration',
                      Div(
                          Div( 'first_name', css_class='col-lg-5' ),
                          Div( 'middle_initial', css_class='col-md-2' ),
                          Div( 'last_name', css_class='col-md-5' ),
                          css_class='row',
                      ),
                      Div(
                          Div( 'date_of_birth', css_class='col-lg-3' ),
                          Div( 'gender', css_class='col-md-1' ),
                          css_class='row',
                      ),
                      Div(
                          Div( 'email', css_class='col-lg-5' ),
                          Div( 'password', css_class='col-md-5' ),
                          css_class='row',
                      ),
                      Div(
                          Div( 'height', css_class='col-lg-4' ),
                          Div( 'weight', css_class='col-md-4' ),
                          Div( 'blood_type', css_class='cool-md-2' ),
                          css_class='row',
                      ),
                      'insurance',
                      'pref_hospital',
                      Div(
                          Div( 'security_question', css_class='col-lg-4' ),
                          Div( 'security_answer', css_class='col-md-4' ),
                          css_class='row',
                      ),
                      Div(
                          Div( 'contact_name', css_class='col-lg-5' ),
                          Div( 'contact_relationship', css_class='col-lg-3' ),
                          css_class='row',
                      ),
                      Div(
                          Div( 'contact_email', css_class='col-lg-5' ),
                          css_class='row',
                      ),
                      Div(
                          Div( PrependedText( 'contact_primary', 'contact' ), css_class='col-lg-5' ),
                          Div( 'contact_secondary', css_class='col-lg-5' ),
                          css_class='row'
                      )
                      ),
            FormActions(
                Submit( 'submit', 'Submit' ),
                HTML( '<a class="btn btn-default" href={% url "registry:index" %}>Cancel</a>' )
            )
        )

        self.fields['first_name'].widget.attrs['size'] = 40
        self.fields['last_name'].widget.attrs['size'] = 40
        self.fields['email'].widget.attrs['size'] = 40
        self.fields['password'].widget.attrs['size'] = 40

        self.fields['pref_hospital'].required = False
        self.fields['middle_initial'].required = False
        self.fields['middle_initial'].label = 'M.I.'
        self.fields['middle_initial'].widget.attrs['maxlength'] = 1
        self.fields['middle_initial'].widget.attrs['size'] = 3
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


class LoginForm(forms.Form):
    email = fields.EmailField( )
    password = fields.CharField( max_length=255, widget=widgets.PasswordInput )

    def __init__(self, *args, **kwargs):
        super( LoginForm, self ).__init__( *args, **kwargs )
        self.helper = FormHelper( )
        self.helper.form_class = 'form-horizontal hn-form login'
        self.helper.form_method = 'POST'
        self.helper.form_action = reverse_lazy( 'registry:login' )
        self.helper.label_class = 'control-label col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
            Fieldset( 'HealthNet Login',
                      'email',
                      'password',
                      ),
            FormActions(
                Submit( 'login', 'Log In' ),
                HTML( '<a class="btn btn-default" href={% url "registry:index" %}>Cancel</a>' )
            )
        )


class HospitalRegisterForm(models.ModelForm):
    class Meta:
        model = Hospital
        fields = ('name', 'address', 'state', 'zipcode', 'identifiers')


class AppointmentSchedulingForm(models.ModelForm):
    model = Appointment

    time = DateTimeMultiField()

    def __init__(self, *args, **kwargs):
        super( AppointmentSchedulingForm, self ).__init__( *args, **kwargs )
        self.helper = FormHelper( )
        self.helper.form_class = 'form-horizontal hn-form appointment'
        self.helper.form_method = 'POST'
        self.helper.form_action = reverse_lazy( 'registry:appt_create' )
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
            Fieldset( 'Appointment Scheduling',
                      Div(
                          Div( 'time', css_class='col-lg-3' ),
                          css_class='row',
                      ),
                      'doctor',
                      'patient',
                      'location',
                      ),
            FormActions(
                Submit( 'submit', 'Submit' ),
                HTML(
                    '<a class="btn btn-default" href={% if next_url %}{{ next_url }}{% else %}{% url "registry:calendar" %}{% endif %}>Cancel</a>' )
            )
        )

        self.fields['time'].widget.attrs['timepicker'] = True

    class Meta:
        model = Appointment
        fields = ('time', 'doctor', 'patient', 'location')


class DeleteAppForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = []


class PrescriptionCreation(forms.ModelForm):
    model = Prescription

    start_time = DateTimeMultiField()
    end_time = DateTimeMultiField()

    def __init__(self, *args, **kwargs):
        super(PrescriptionCreation, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form prescription'
        self.helper.form_method = 'POST'
        self.helper.form_action = reverse_lazy('registry:pre_create')
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
            Fieldset('Prescription Creation',
                     'drug',
                     'patient',
                     'doctor',
                     'count',
                     'amount',
                     'refills',
                     Div(
                          Div('start_time', css_class='col-lg-3'),
                          css_class='row',
                      ),
                     Div(
                          Div('end_time', css_class='col-lg-3'),
                          css_class='row',
                      ),
                     ),
            FormActions(
                Submit('submit', 'Submit'),
                HTML(
                    '<a class="btn btn-default" href={% if next_url %}{{ next_url }}{% else %}{% url "registry:pre_create" %}{% endif %}>Cancel</a>' )
            )
        )

        self.fields['start_time'].widget.attrs['timepicker'] = True
        self.fields['end_time'].widget.attrs['timepicker'] = True

    class Meta:
        model = Prescription
        fields = 'drug', 'patient', 'doctor', 'count', 'amount', 'refills'

class MessageCreation(forms.ModelForm):
    model = Message

    to = fields.EmailField()

    def __init__(self, *args, **kwargs):
        super(MessageCreation,self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form messsage'
        self.helper.form_method = 'POST'
        self.helper.form_action = reverse_lazy('')
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
            Fieldset('New Message',
                     'to',
                     'content',
                     Div(
                         Div('to', css_class='col-lg-3'),
                         css_class= 'row',
                     ),
                     Div(
                         Div('content', css_class='col-lg-3'),
                         css_class= 'row',
                     ),
            ),
            FormActions(
                Submit('submit','Submit'),
                HTML('<a class="btn btn-default" href={% if next_url %}{{ next_url }}{% else %}{% url "registry:home" %}{% endif %}>Cancel</a>')
            )
        )
    class Meta:
        model = Message
        fields = 'receiver', 'sender', 'content'