from .models import *
from .utility.options import *
from .utility.widgets import HeightField, WeightField, DateTimeMultiField

from crispy_forms.bootstrap import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django.core.urlresolvers import reverse_lazy
from localflavor.us.forms import USPhoneNumberField
from localflavor.us.forms import USZipCodeField
from localflavor.us.forms import USStateSelect
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
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
                Fieldset('Patient Registration',
                         Div(
                                 Div('first_name', css_class='col-lg-5'),
                                 Div('middle_initial', css_class='col-md-2'),
                                 Div('last_name', css_class='col-md-5'),
                                 css_class='row',
                         ),
                         Div(
                                 Div('date_of_birth', css_class='col-lg-3'),
                                 Div('gender', css_class='col-md-1'),
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
                  'email', 'password', 'height', 'weight', 'blood_type',
                  'insurance', 'pref_hospital', 'provider', 'security_question', 'security_answer')
        widgets = {
            'password': widgets.PasswordInput
        }


class StaffRegistrationForm(forms.Form):
    """
    Name: StaffRegistrationForm

    It's a form that allows admin users to create a new staff user.
    """

    first_name = fields.CharField(max_length=25)
    middle_initial = fields.CharField(max_length=1)
    last_name = fields.CharField(max_length=30)

    email = fields.EmailField()
    password = fields.CharField(max_length=255, widget=widgets.PasswordInput)

    date_of_birth = fields.DateTimeField()
    gender = fields.ChoiceField(choices=Gender.choices(), initial=Gender.MALE)
    role = fields.ChoiceField(choices=Role.choices(), initial=Role.DOCTOR)

    address_line_one = fields.CharField(max_length=255)
    address_line_two = fields.CharField(max_length=255)
    address_city = fields.CharField(max_length=255)
    address_state = USStateSelect()
    address_zipcode = USZipCodeField()

    def __init__(self, *args, **kwargs):
        super(StaffRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form login'
        self.helper.form_method = 'POST'
        self.helper.label_class = 'control-label col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
            Fieldset('Staff Registration',
                     Div(
                        Div('name_prefix', css_class='col-lg-2'),
                        Div('first_name', css_class='col-lg-2'),
                        Div('middle_initial', css_class='col-md-2'),
                        Div('last_name', css_class='col-md-2'),
                        Div('name_suffix', css_class='col-lg-2'),
                        css_class='row',
                     ),
                     Div(
                         Div('email', css_class='col-lg-3'),
                         Div('password', css_class='col-lg-3')
                     ),
                     Div(
                        Div('date_of_birth', css_class='col-lg-5'),
                        Div('gender', css_class='col-lg-3'),
                        Div('Role', css_class='col-lg-3'),
                        css_class='row',
                     ),
                     Div(
                        Div('address_line_one', css_class='col-lg-5'),
                        Div('address_line_two', css_class='col-lg-5'),
                        css_class='row',
                     ),
                     Div(
                        Div('address_city', css_class='col-lg-5'),
                        Div('address_state', css_class='col-lg-5'),
                        Div('address_zipcode', css_class='col-lg-5'),
                        css_class='row',
                     )
                    ),
            FormActions(
                Submit('submit', 'Submit'),
                HTML('<a class="btn btn-default" href={% url "registry:home" %}>Cancel</a>')
            )
        )

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
                                '{% url "registry:calendar" %}{% endif %}>Cancel</a>')
                )
        )
        if rules.test_rule('is_patient', user):
            self.fields['patient'].queryset = Patient.objects.get(uuid=user.uuid)
            self.fields['doctor'].queryset = Patient.objects.get(uuid=user.uuid).provider
        elif rules.test_rule('is_doctor', user):
            self.fields['patient'].queryset = Patient.objects.filter(provider=user)
        elif rules.test_rule('is_nurse', user):
            self.fields['patient'].queryset = Patient.objects.filter(pref_hospital=user.hospital)
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
                                '{% url "registry:calendar" %}{% endif %}>Cancel</a> '
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


class DeletePresForm(models.ModelForm):
    """
    Name: DeletePresForm

    Deletion of Pres form
    """

    class Meta:
        model = Prescription
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
        doctor = kwargs.pop('user')
        super(PrescriptionCreation, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal hn-form prescription'
        self.helper.form_method = 'POST'
        # self.helper.form_action = reverse_lazy('registry:pres_create')
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
                Fieldset('Prescription Creation',
                         'drug',
                         'patient',
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
                                '<a class="btn btn-default" href={% if next_url %}{{ next_url }}{% else %}'
                                '{% url "registry:pres_create" %}{% endif %}>Cancel</a>'
                        )
                )
        )

        self.fields['patient'].queryset = Patient.objects.filter(provider=doctor)
        self.fields['start_time'].widget.attrs['timepicker'] = True
        self.fields['end_time'].widget.attrs['timepicker'] = True

    class Meta:
        model = Prescription
        fields = 'drug', 'patient', 'count', 'amount', 'refills'
        exclude = ['doctor']


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
        # self.helper.form_action = reverse_lazy('')
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
                Fieldset('New Message',
                         Div(
                                 Div('receiver', css_class='col-lg-3'),
                                 css_class='row',
                         ),
                         Div(
                                 Div('content', css_class='col-lg-3'),
                                 css_class='row',
                         ),
                         ),
                FormActions(
                        Submit('submit', 'Submit'),
                        HTML(
                                '<a class="btn btn-default" href={% if next_url %}{{ next_url }}{% else %}{% url "registry:home" %}{% endif %}>Cancel</a>')
                )
        )

    class Meta:
        model = Message
        fields = 'receiver', 'content'
