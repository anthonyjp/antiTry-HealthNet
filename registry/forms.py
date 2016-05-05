from .models import *

from .utility.options import *
from .utility.widgets import HeightField, WeightField, DateTimeMultiField

from crispy_forms.bootstrap import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django.core.urlresolvers import reverse_lazy
from localflavor.us.forms import USPhoneNumberField
from django.forms import forms, models, fields, widgets

import rules

class PatientRegisterForm(models.ModelForm):
    """
    Name: PatientRegisterForm

    It's a patient registration form based on the Patient Model.
    """
    model = Patient
    first_name = fields.CharField(max_length=25)
    last_name = fields.CharField(max_length=30)
    password = fields.CharField(max_length=40, widget=widgets.PasswordInput)
    email = fields.EmailField(max_length=256)
    height = HeightField(required=True)
    weight = WeightField(required=True)

    address_line_two = fields.CharField(required=False)
    contact_name = fields.CharField(max_length=60)
    contact_relationship = fields.ChoiceField(choices=Relationship.choices(), initial=Relationship.OTHER)
    contact_primary = USPhoneNumberField(required=True)
    contact_secondary = USPhoneNumberField(required=False)
    contact_email = fields.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super(PatientRegisterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form register'
        self.helper.form_method = 'POST'
        self.helper.form_action = 'register'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-2'

        self.helper.layout = Layout(
                Fieldset('Patient Registration',
                         Div(
                             Div('first_name', css_class='col-md-4'),
                             Div('middle_initial', css_class='col-xs-1'),
                             Div('last_name', css_class='col-md-4'),
                             css_class='row',
                         ),
                         Div(
                                 Div('date_of_birth', css_class='col-lg-3'),
                                 Div('gender', css_class='col-md-1'),
                                 css_class='row',
                         ),
                         Div(
                             Div('address_line_one', css_class='col-lg-5'),
                             css_class='row',
                         ),
                         Div(
                             Div('address_line_two', css_class='col-lg-5'),
                             css_class='row',
                         ),
                         Div(
                             Div('address_city', css_class='col-lg-3'),
                             Div('address_state', css_class='col-lg-3'),
                             Div('address_zipcode', css_class='col-lg-3'),
                             css_class='row',
                         ),
                         Div(
                                 Div('email', css_class='col-lg-5'),
                                 Div('password', css_class='col-md-5'),
                                 css_class='row',
                         ),
                         Div(
                                 Div('height', css_class='col-lg-4'),
                                 Div('weight', css_class='col-md-4'),
                                 Div('blood_type', css_class='cool-md-2'),
                                 css_class='row',
                         ),
                         'insurance',
                         Div(
                                 Div('security_question', css_class='col-lg-4'),
                                 Div('security_answer', css_class='col-md-4'),
                                 css_class='row',
                         ),
                         'pref_hospital',
                         'provider',
                         Div(
                                 Div('contact_name', css_class='col-lg-5'),
                                 Div('contact_relationship', css_class='col-lg-3'),
                                 css_class='row',
                         ),
                         Div(
                                 Div('contact_email', css_class='col-lg-5'),
                                 css_class='row',
                         ),
                         Div(
                                 Div(PrependedText('contact_primary', 'contact'), css_class='col-lg-5'),
                                 Div('contact_secondary', css_class='col-lg-5'),
                                 css_class='row'
                         )
                         ),
                FormActions(
                        Submit('submit', 'Submit'),
                        HTML('<a class="btn btn-default" href={% url "registry:index" %}>Cancel</a>')
                )
        )

        self.fields['first_name'].widget.attrs['size'] = 40
        self.fields['last_name'].widget.attrs['size'] = 40
        self.fields['email'].widget.attrs['size'] = 40
        self.fields['password'].widget.attrs['size'] = 40

        self.fields['address_line_one'].widget.attrs['size'] = 45
        self.fields['address_line_two'].widget.attrs['size'] = 45

        self.fields['pref_hospital'].required = False
        self.fields['provider'].required = False
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
                  'address_line_one', 'address_line_two', 'address_city', 'address_state',
                  'address_zipcode', 'email', 'password', 'height', 'weight', 'blood_type',
                  'insurance', 'pref_hospital', 'provider', 'security_question', 'security_answer')
        widgets = {
            'password': widgets.PasswordInput
        }


class AdminRegistrationForm(models.ModelForm):
    """
    Name: PatientRegisterForm

    It's a patient registration form based on the Patient Model.
    """
    model = Administrator
    first_name = fields.CharField(max_length=25)
    last_name = fields.CharField(max_length=30)
    password = fields.CharField(max_length=40, widget=widgets.PasswordInput)
    email = fields.EmailField(max_length=256)

    def __init__(self, *args, **kwargs):
        super(AdminRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form register'
        self.helper.form_method = 'POST'
        self.helper.form_action = 'register'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-2'

        self.helper.layout = Layout(
            Fieldset('Administrator Registration',
                     Div(
                         Div('first_name', css_class='col-md-4'),
                         Div('middle_initial', css_class='col-xs-1'),
                         Div('last_name', css_class='col-md-4'),
                         css_class='row',
                     ),
                     Div(
                         Div('date_of_birth', css_class='col-lg-3'),
                         Div('gender', css_class='col-md-1'),
                         css_class='row',
                     ),
                     Div(
                         Div('address_line_one', css_class='col-lg-5'),
                         css_class='row',
                     ),
                     Div(
                         Div('address_line_two', css_class='col-lg-5'),
                         css_class='row',
                     ),
                     Div(
                         Div('address_city', css_class='col-lg-3'),
                         Div('address_state', css_class='col-lg-3'),
                         Div('address_zipcode', css_class='col-lg-3'),
                         css_class='row',
                     ),
                     Div(
                         Div('email', css_class='col-lg-5'),
                         Div('password', css_class='col-md-5'),
                         css_class='row',
                     ),
                     Div(
                         Div('security_question', css_class='col-lg-4'),
                         Div('security_answer', css_class='col-md-4'),
                         css_class='row',
                     ),
                     'hospital',
                     'is_sysadmin',
                     ),
        )

        self.fields['first_name'].widget.attrs['size'] = 40
        self.fields['last_name'].widget.attrs['size'] = 40
        self.fields['email'].widget.attrs['size'] = 40
        self.fields['password'].widget.attrs['size'] = 40

        self.fields['address_line_one'].widget.attrs['size'] = 45
        self.fields['address_line_two'].widget.attrs['size'] = 45
        self.fields['address_line_two'].required = False
        self.fields['middle_initial'].required = False
        self.fields['middle_initial'].label = 'M.I.'
        self.fields['middle_initial'].widget.attrs['maxlength'] = 1
        self.fields['middle_initial'].widget.attrs['size'] = 3
        self.fields['date_of_birth'].widget.attrs['datepicker'] = True

    class Meta:
        model = Administrator
        fields = ('first_name', 'middle_initial', 'last_name', 'date_of_birth', 'gender',
                  'address_line_one', 'address_line_two', 'address_city', 'address_state',
                  'address_zipcode', 'email', 'password', 'security_question',
                  'security_answer', 'is_sysadmin', 'hospital')
        widgets = {
            'password': widgets.PasswordInput
        }


class DoctorRegistrationForm(models.ModelForm):
    model = Doctor
    first_name = fields.CharField(max_length=25)
    last_name = fields.CharField(max_length=30)
    password = fields.CharField(max_length=40, widget=widgets.PasswordInput)
    email = fields.EmailField(max_length=256)

    def __init__(self, *args, **kwargs):
        super(DoctorRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form register'
        self.helper.form_method = 'POST'
        self.helper.form_action = 'register'

        self.helper.layout = Layout(
            Fieldset('Doctor Registration',
                     Div(
                         Div('first_name', css_class='col-lg-4'),
                         Div('middle_initial', css_class='col-lg-2'),
                         Div('last_name', css_class='col-lg-4'),
                         css_class='row',
                     ),
                     Div(
                         Div('date_of_birth', css_class='col-lg-5'),
                         Div('gender', css_class='col-lg-6'),
                         css_class='row',
                     ),
                     Div(
                         Div('address_line_one', css_class='col-lg-12'),
                         css_class='row',
                     ),
                     Div(
                         Div('address_line_two', css_class='col-lg-12'),
                         css_class='row',
                     ),
                     Div(
                         Div('address_city', css_class='col-lg-4'),
                         Div('address_state', css_class='col-lg-4'),
                         Div('address_zipcode', css_class='col-lg-4'),
                         css_class='row',
                     ),
                     Div(
                         Div('email', css_class='col-lg-6'),
                         Div('password', css_class='col-lg-6'),
                         css_class='row',
                     ),
                     Div(
                         Div('security_question', css_class='col-lg-6'),
                         Div('security_answer', css_class='col-lg-6'),
                         css_class='row',
                     ),
                     Div('hospitals', css_class='col-lg-12'),
                     css_class='row',
                     ),
        )

        self.fields['first_name'].widget.attrs['size'] = 50
        self.fields['last_name'].widget.attrs['size'] = 40
        self.fields['email'].widget.attrs['size'] = 40
        self.fields['password'].widget.attrs['size'] = 40

        self.fields['address_line_one'].widget.attrs['size'] = 45
        self.fields['address_line_two'].widget.attrs['size'] = 45
        self.fields['address_line_two'].required = False

        self.fields['middle_initial'].required = False
        self.fields['middle_initial'].label = 'M.I.'
        self.fields['middle_initial'].widget.attrs['maxlength'] = 1
        self.fields['middle_initial'].widget.attrs['size'] = 3
        self.fields['date_of_birth'].widget.attrs['datepicker'] = True

    class Meta:
        model = Doctor
        fields = ('first_name', 'middle_initial', 'last_name', 'date_of_birth', 'gender',
                  'address_line_one', 'address_line_two', 'address_city', 'address_state',
                  'address_zipcode', 'email', 'password', 'security_question',
                  'security_answer', 'hospitals')
        widgets = {
            'password': widgets.PasswordInput
        }


class NurseRegistrationForm(models.ModelForm):
    model = Nurse
    first_name = fields.CharField(max_length=25)
    last_name = fields.CharField(max_length=30)
    password = fields.CharField(max_length=40, widget=widgets.PasswordInput)
    email = fields.EmailField(max_length=256)

    def __init__(self, *args, **kwargs):
        super(NurseRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form register'
        self.helper.form_method = 'POST'
        self.helper.form_action = 'register'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
            Fieldset('Nurse Registration',
                     Div(
                         Div('first_name', css_class='col-md-4'),
                         Div('middle_initial', css_class='col-xs-1'),
                         Div('last_name', css_class='col-md-4'),
                         css_class='row',
                     ),
                     Div(
                         Div('date_of_birth', css_class='col-lg-3'),
                         Div('gender', css_class='col-md-1'),
                         css_class='row',
                     ),
                     Div(
                         Div('address_line_one', css_class='col-lg-5'),
                         css_class='row',
                     ),
                     Div(
                         Div('address_line_two', css_class='col-lg-5'),
                         css_class='row',
                     ),
                     Div(
                         Div('address_city', css_class='col-lg-3'),
                         Div('address_state', css_class='col-lg-3'),
                         Div('address_zipcode', css_class='col-lg-3'),
                         css_class='row',
                     ),
                     Div(
                         Div('email', css_class='col-lg-5'),
                         Div('password', css_class='col-md-5'),
                         css_class='row',
                     ),
                     Div(
                         Div('security_question', css_class='col-lg-4'),
                         Div('security_answer', css_class='col-md-4'),
                         css_class='row',
                     ),
                     'hospital',
                     ),
        )

        self.fields['first_name'].widget.attrs['size'] = 40
        self.fields['last_name'].widget.attrs['size'] = 40
        self.fields['email'].widget.attrs['size'] = 40
        self.fields['password'].widget.attrs['size'] = 40

        self.fields['address_line_one'].widget.attrs['size'] = 45
        self.fields['address_line_two'].widget.attrs['size'] = 45
        self.fields['address_line_two'].required = False

        self.fields['middle_initial'].required = False
        self.fields['middle_initial'].label = 'M.I.'
        self.fields['middle_initial'].widget.attrs['maxlength'] = 1
        self.fields['middle_initial'].widget.attrs['size'] = 3
        self.fields['date_of_birth'].widget.attrs['datepicker'] = True

    class Meta:
        model = Nurse
        fields = ('first_name', 'middle_initial', 'last_name', 'date_of_birth', 'gender',
                  'address_line_one', 'address_line_two', 'address_city', 'address_state',
                  'address_zipcode', 'email', 'password', 'security_question',
                  'security_answer', 'hospital')
        widgets = {
            'password': widgets.PasswordInput
        }


class LoginForm(forms.Form):
    """
    Name:   LoginForm

    It's a form that allows users to log into the system
    """
    email = fields.EmailField()
    password = fields.CharField(max_length=255, widget=widgets.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form login'
        self.helper.form_method = 'POST'
        self.helper.form_action = reverse_lazy('registry:login')
        self.helper.label_class = 'control-label col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
                Fieldset('HealthNet Login',
                         'email',
                         'password',
                         ),
                FormActions(
                        Submit('login', 'Log In'),
                        HTML('<a class="btn btn-default" href={% url "registry:index" %}>Cancel</a>')
                )
        )


class HospitalRegisterForm(models.ModelForm):
    """
    Name:   HospitalRegisterForm

    Hospital registration form based on the Hospital model
    """

    class Meta:
        model = Hospital
        fields = ('name', 'address', 'state', 'zipcode', 'identifiers')


class AppointmentSchedulingForm(models.ModelForm):
    """
    Name:   AppointmentSchedulingForm

    It's a form for appointment scheduling based on the Appointment model
    """

    model = Appointment
    time = DateTimeMultiField()

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(AppointmentSchedulingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form appointment'
        self.helper.form_method = 'POST'
        self.helper.form_action = reverse_lazy('registry:appt_create')
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
                Fieldset('Appointment Scheduling',
                         Div(
                                 Div('time', css_class='col-lg-3'),
                                 css_class='row',
                         ),
                         'doctor',
                         'patient',
                         'location',
                         ),
                FormActions(
                        Submit('submit', 'Submit'),
                        HTML(
                                '<a class="btn btn-default" href={% if next_url %}{{ next_url }}{% else %}'
                                '{% url "registry:home" %}{% endif %}>Cancel</a>')
                )
        )
        if rules.test_rule('is_patient', user):
            self.fields['patient'].queryset = Patient.objects.filter(uuid=user.uuid)
        # elif rules.test_rule('is_doctor', user):
        #    self.fields['patient'].queryset = Patient.objects.filter(provider=user)
        # elif rules.test_rule('is_nurse', user):
        #    self.fields['patient'].queryset = Patient.objects.filter(pref_hospital=user.hospital)
        self.fields['time'].widget.attrs['timepicker'] = True

    class Meta:
        model = Appointment
        fields = ('time', 'doctor', 'patient', 'location')


class AppointmentEditForm(models.ModelForm):
    """
    Name:   AppointmentSchedulingForm

    It's a form for appointment scheduling based on the Appointment model
    """

    model = Appointment
    time = DateTimeMultiField()

    def __init__(self, *args, **kwargs):
        appt_id = kwargs.pop('appt_id')
        hospital = Appointment.objects.get(pk=appt_id).doctor.hospitals
        super(AppointmentEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form appointment'
        self.helper.form_method = 'POST'
        # self.helper.form_action = reverse_lazy('registry:appt_edit')
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
                Fieldset('Appointment Editing',
                         Div(
                                 Div('time', css_class='col-lg-3'),
                                 css_class='row',
                         ),
                         'location',
                         ),
                FormActions(
                        Submit('submit', 'Submit'),
                        HTML(
                                '<a class="btn btn-default" href={% if next_url %}{{ next_url }}{% else %}'
                                '{% url "registry:home" %}{% endif %}>Cancel</a> '
                        )
                )
        )

        self.fields['location'].queryset = hospital
        self.fields['time'].widget.attrs['timepicker'] = True

    class Meta:
        model = Appointment
        fields = ('time', 'location')


class DeleteAppForm(models.ModelForm):
    """
    Name: DeleteAppForm

    Deletion of Appointment form
    """

    class Meta:
        model = Appointment
        fields = []


class PrescriptionCreation(models.ModelForm):
    """
    Name: PrescriptionCreation

    Prescription Creation form based on the model Prescription
    Doctors are limited to patients that have him/her as provider
    """
    model = Prescription

    start_time = DateTimeMultiField()
    end_time = DateTimeMultiField()

    def __init__(self, *args, **kwargs):
        patient = kwargs.pop('uuid')
        super(PrescriptionCreation, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form prescription'
        self.helper.form_method = 'POST'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
                Fieldset('Prescription Creation',
                         Div(
                             Div('drug', css_class='col-lg-3'),
                             css_class='row',
                         ),
                         Div(
                             Div('patient', css_class='col-lg-3'),
                             css_class='row',
                         ),
                         Div(
                             Div('count', css_class='col-lg-3'),
                             Div('amount', css_class='col-lg-3'),
                             Div('refills', css_class='col-lg-3'),
                             css_class='row',
                         ),
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
                                '<a class="btn btn-default" href={% if next_url %}{{ next_url }}{% else %}'
                                '{% url "registry:home" %}{% endif %}>Cancel</a>'
                        )
                )
        )

        self.fields['patient'].queryset = Patient.objects.filter(uuid=patient)
        self.fields['start_time'].widget.attrs['timepicker'] = True
        self.fields['end_time'].widget.attrs['timepicker'] = True

    class Meta:
        model = Prescription
        fields = 'drug', 'patient', 'count', 'amount', 'refills'
        exclude = ['doctor']


class DeletePresForm(models.ModelForm):
    """
    Name: DeletePresForm

    Deletion of Pres form
    """

    class Meta:
        model = Prescription
        fields = []


class PatientAdmitForm(models.ModelForm):
    """
    Name: PatientAdmitForm

    AdmitPatient is the form for admitting a patient to a hospital.
    This form will only allow the user to chose the hospital and
    the reason why the patient is in the hospital.
    All other fields will be set in the view.

    """
    model = AdmissionInfo

    def __init__(self, *args, **kwargs):
        super(PatientAdmitForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form admittance'
        self.helper.form_method = 'POST'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            Fieldset('Patient Admit Form',
                     'hospital',
                     'doctor',
                     'reason'
                     ),
            FormActions(
                Submit('submit', 'Submit'),
                HTML(
                    '<a class="btn btn-default" href={% if next_url %}{{ next_url }}{% else %}'
                    '{% url "registry:home" %}{% endif %}>Cancel</a>'
                )
            )
        )


    class Meta:
        model = AdmissionInfo
        fields = 'hospital', 'doctor', 'reason',
        exclude = ['patient', 'admitted_by', 'admission_time']


class DischargeForm(models.ModelForm):
    """
    Name: DischargeForm

    Discharge form
    """

    class Meta:
        model = AdmissionInfo
        fields = []


class PatientTransferForm(models.ModelForm):
    """
    Name: PatientTransferForm

    TransferPatient is the form for requesting a patient to transfer to another hospital.
    This form will only allow the user to chose the hospital and
    the reason why the patient is in the hospital.
    All other fields will be set in the view.

    """
    model = AdmissionInfo

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(PatientTransferForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form admittance'
        self.helper.form_method = 'POST'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            Fieldset('Patient Transfer Form',
                     'doctor',
                     'hospital',
                     'reason'
                     ),
            FormActions(
                Submit('submit', 'Submit'),
                HTML(
                    '<a class="btn btn-default" href={% if next_url %}{{ next_url }}{% else %}'
                    '{% url "registry:home" %}{% endif %}>Cancel</a>'
                )
            )
        )
        # Filter the fields for doctor and hospital based on the user requesting transfer
        # A doctor will see his name and the hospital he works at
        # An admin will see his hospital and the doctors that work there
        if rules.test_rule('is_doctor', user):
            self.fields['doctor'].queryset = Doctor.objects.filter(uuid=user.uuid)
            self.fields['hospital'].queryset = user.hospitals.all()
        elif rules.test_rule('is_administrator', user):
            self.fields['doctor'].queryset = Doctor.objects.filter(hospitals__name__exact=user.hospital.name)
            self.fields['hospital'].queryset = Hospital.objects.filter(name=user.hospital.name)


    class Meta:
        model = AdmissionInfo
        fields = 'doctor', 'hospital', 'reason'
        exclude = ['patient', 'admitted_by']


class MedicalConditionAdd(models.ModelForm):
    """
    Name: MedicalConditionAdd

    MedicalConditionAdd is for adding a new medical condition to a patient
    It takes in the name of the condition and the description of the condition

    """
    model = MedicalCondition

    def __init__(self, *args, **kwargs):
        super(MedicalConditionAdd, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form admittance'
        self.helper.form_method = 'POST'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            Fieldset('Medical Condition Form',
                     'name',
                     'desc',
                     ),
            FormActions(
                Submit('submit', 'Submit'),
                HTML(
                    '<a class="btn btn-default" href={% if next_url %}{{ next_url }}{% else %}'
                    '{% url "registry:home" %}{% endif %}>Cancel</a>'
                )
            )
        )

    class Meta:
        model = MedicalCondition
        fields = 'name', 'desc'


class MessageCreation(models.ModelForm):
    """
    Name: MessageCreation

    Message Creation form based on the model Message
    """

    model = Message

    def __init__(self, *args, **kwargs):
        super(MessageCreation, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form messsage'
        self.helper.form_method = 'POST'
        self.helper.label_class = 'col-lg-8'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
                Fieldset('New Message',
                         Div(
                                 Div('receiver', css_class='col-lg-3'),
                                 css_class='row',
                         ),
                         Div(
                             Div('title', css_class='col-lg-3'),
                             css_class='row',
                         ),
                         Div(
                                 Div('content', css_class='col-lg-3'),
                                 css_class='row',
                         ),
                         )
        )
        self.fields['title'].widget.attrs['size'] = 30
        self.fields['title'].widget.attrs['style'] = ""

    class Meta:
        model = Message
        fields = 'receiver', 'content', 'title'


class TimeFrame(forms.Form):
    start = fields.DateField()
    end = fields.DateField()

    def __init__(self, *args, **kwargs):
        super(TimeFrame, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form timeFrame'
        self.helper.form_method = 'POST'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
            Fieldset('Time Frame',
                     Div(
                         Div('start', css_class='col-lg-3'),
                         css_class='row',
                     ),
                     Div(
                         Div('end', css_class='col-lg-3'),
                         css_class='row',
                     ),
                     ),
            FormActions(
                Submit('submit', 'Submit'),
            )
        )

        self.fields['start'].widget.attrs['datepicker'] = True
        self.fields['end'].widget.attrs['datepicker'] = True
