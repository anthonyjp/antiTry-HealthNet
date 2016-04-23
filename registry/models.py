import uuid
import rules
import django.utils.timezone as tz

from datetime import datetime
from annoying import fields

from django.contrib.auth.models import User as DjangoUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from localflavor.us.models import PhoneNumberField
from localflavor.us.us_states import STATE_CHOICES
from registry.utility.options import Relationship
from model_utils.managers import InheritanceManager

from registry.utility.options import BloodType, Gender, INSURANCE_CHOICES, AdmitOptions, LogAction
from registry.utility.options import SecurityQuestion as SecQ
from registry.utility.models import TimeRange, Dictionary, SeparatedValuesField

DjangoUser.USERNAME_FIELD = 'email'
DjangoUser.REQUIRED_FIELDS = ['username']
DjangoUser._meta.get_field('username')._unique = False
DjangoUser._meta.get_field('email')._unique = True


### General Data Models
class Hospital(models.Model):
    """
    Represents a hospital with a location
    """

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=300)
    state = models.CharField(max_length=2, choices=STATE_CHOICES, blank=False, null=False)
    zipcode = models.CharField(max_length=10, blank=False, null=False)
    identifiers = models.ForeignKey(default=Dictionary.empty, to=Dictionary, on_delete=models.SET(Dictionary.empty))

    def get_location(self):
        """
        Returns the location of the hospital as combined location fields of the form:

        <address>, <state> <zipcode>
        :return: Location
        """
        return "%s, %s %s" % (self.address, self.state, self.zipcode)

    # TODO get coordinates
    def get_coordinates(self):
        """
        Returns the Latitutde and Longitude of the hospital, if possible, as a Tuple of two floats. If the location
        can not be determined the Tuple contains Not-a-Number.

        :return: (latitude,longitude)
        """
        return float('NaN'), float('NaN')

    def __str__(self):
        return self.name


class Drug(models.Model):
    """
    A drug model consisting of a name, the providers which are the company name, the side effects, and the msds link
    """
    name = models.CharField(max_length=255)
    # The company name, can have multiple
    providers = SeparatedValuesField()
    # Multiple side effects separated by commas
    side_effects = SeparatedValuesField()
    msds_link = models.CharField(max_length=512, null=True)

    def __str__(self):
        return self.name


### User Models
class User(models.Model):
    """
    A Generic User account that extends Django's Auth User account (for authentication use) also consisting of a
    first name, last name, password and email.
    """
    auth_user = models.OneToOneField(to=DjangoUser, on_delete=models.CASCADE, related_name='hn_user')
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    first_name = models.CharField(max_length=255, default='John/Jane')
    middle_initial = models.CharField(max_length=1, blank=True, default='')
    last_name = models.CharField(max_length=255, default='Doe')
    date_of_birth = models.DateField()
    gender = models.SmallIntegerField(choices=Gender.choices(), default=Gender.MALE)
    security_question = models.SmallIntegerField(choices=SecQ.choices(), default=SecQ.Q1)
    security_answer = models.CharField(max_length=50, null=False, blank=False)

    address_line_one = models.CharField(max_length=255, default='')
    address_line_two = models.CharField(max_length=255, default='', null=True)
    address_city = models.CharField(max_length=255, default='')
    address_state = models.CharField(max_length=2, choices=STATE_CHOICES, blank=False, null=False)
    address_zipcode = models.CharField(max_length=255, default='')

    objects = InheritanceManager()

    def has_perm(self, perm, *args, **kwargs):
        return rules.has_perm(perm, self, *args, **kwargs)

    def has_module_perms(self, app_label):
        return rules.has_perm(app_label, self)

    def get_user_type(self):
        return 'Generic User'

    def __str__(self):
        if self.middle_initial:
            return "%s %s. %s" % (self.first_name, self.middle_initial, self.last_name)
        else:
            return "%s %s" % (self.first_name, self.last_name)

    def __repr__(self):
        return "%s [%s]" % (str(self), str(self.uuid))


class Doctor(User):
    """
    A doctor account that extends User consisting of a set of Hospitals
    """
    hospitals = models.ManyToManyField(Hospital, related_name='provider_to')

    def get_user_type(self):
        return 'Doctor'

    def __str__(self):
        return "Dr. %s" % (super(Doctor, self).__str__())


class Nurse(User):
    """
    A nurse account that extends User consisting of one Hospital
    """
    hospital = models.ForeignKey(Hospital)

    def get_user_type(self):
        return 'Nurse'

    def __str__(self):
        return "%s RN" % (super(Nurse, self).__str__())


class AdmissionInfo(models.Model):
    """
    Admission info is an object that consists of the patient as a text field, admitted by which is the string
    of the user who is submitting the admit, the hospital that the patient will stay at, the reason which is an
    option from the preset enum, and the admission time which start time will be set in the view and the end
    date will be set when patient is transferred or discharged
    """
    reason = models.SmallIntegerField(choices=AdmitOptions.choices(), default=AdmitOptions.UNKNOWN)
    admission_time = models.OneToOneField(to=TimeRange, on_delete=models.SET_NULL, null=True)
    hospital = models.ForeignKey(to=Hospital)
    doctor = models.ForeignKey('Doctor')

    def end_admission(self):
        if self.medicalhistory:
            history = self.medicalhistory
            self.medicalhistory = None
            history.delete()

        self.admission_time.end_time = tz.now()
        MedicalHistory.objects.create(patient=self.patient_user, admission_details=self)
        self.save()

    def __str__(self):
        return "Admitted by %s to %s on %s" % \
               (self.doctor, self.hospital, self.admission_time.start_time)


class TransferInfo(models.Model):
    """
    Transfer info is an object that consists of the patient as a text field, admitted by which is the string
    of the user who is submitting the transfer, the hospital that the patient will stay at, and the reason which is an
    option from the preset enum
    Similar to the Admission Info except missing the admission_time
    """
    patient = models.TextField()
    admitted_by = models.TextField()
    doctor = models.ForeignKey('Doctor')
    hospital = models.ForeignKey(Hospital)
    reason = models.SmallIntegerField(choices=AdmitOptions.choices(), default=AdmitOptions.EMERGENCY)

    def __str__(self):
        return "%s is being request to transfer to %s by %s" % \
               (self.patient, self.hospital, self.admitted_by)


class Patient(User):
    """
    A patient account that extends User and has multiple fields for the medical infomation and personal information
    of a patient.
    """
    height = models.PositiveIntegerField()
    weight = models.PositiveIntegerField()

    provider = models.ForeignKey(to=Doctor, related_name='providers', on_delete=models.SET_NULL, null=True)
    admission_status = models.OneToOneField(to=AdmissionInfo, related_name='patient_user', on_delete=models.SET_NULL,
                                            null=True)
    pref_hospital = models.ForeignKey(to=Hospital, related_name='%(app_label)s_%(class)s_pref_hospital',
                                      on_delete=models.SET_NULL, null=True)
    transfer_status = models.OneToOneField(to=TransferInfo, related_name='patient_transfer_status',
                                           on_delete=models.SET_NULL, null=True)
    blood_type = models.SmallIntegerField(choices=BloodType.choices(), default=BloodType.UNKNOWN)
    insurance = models.CharField(max_length=40, choices=INSURANCE_CHOICES, default=INSURANCE_CHOICES[0][0])

    conditions = models.ManyToManyField(to='MedicalCondition')

    def get_user_type(self):
        return 'Patient'

    def is_admitted(self):
        return self.admission_status is not None

    def transfer_requested(self):
        return self.transfer_status


class Administrator(User):
    """
    An administer account that extends User consisting of a boolean field of whether or not the administer is
    a system admin and the hospital they belong to
    """
    is_sysadmin = models.BooleanField(default=False)
    hospital = models.ForeignKey(to=Hospital, related_name='admin_to', null=True)
    # null is true just because we have existing admins before the hospital field was added

    def get_user_type(self):
        return 'Administrator'


class MedicalCondition(models.Model):
    """
    Medical condition is an object that consists of the name of the overall condition and then a brief
    description of the condition. For example, a Patient may have cancer and then the description would like
    'a disease caused by an uncontrolled division of abnormal cells in a part of the body'
    """
    name = models.CharField(max_length=200)
    desc = models.TextField()

    def __str__(self):
        return self.name + ": " + self.desc


class Prescription(models.Model):
    """
    A  prescription model that consists of the drug, which is a drop down choice from the created drug
    objects that a sysadmin will create and add onto, the patient who is being prescribed, the doctor issuing
    the prescription, the count which is the pill count, amount which is the milligram amount of the one pill,
    the number of refills, and the time range of the prescription
    """
    drug = models.ForeignKey(to=Drug, on_delete=models.PROTECT)

    patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True)
    doctor = models.ForeignKey(to=Doctor, on_delete=models.CASCADE)

    count = models.PositiveIntegerField()  # prescription count (usually pill count)
    amount = models.PositiveIntegerField()  # milligrams
    refills = models.PositiveIntegerField()

    time_range = models.OneToOneField(to=TimeRange, on_delete=models.PROTECT)

    def __str__(self):
        return "%s at %d dosage for %s prescribed by %s" % (str(self.drug), self.amount, str(self.patient),
                                                            str(self.doctor))

    def is_valid(self):
        return not self.time_range.is_elapsed()


### Patient Data Models

class Appointment(models.Model):
    """
    An appointment in which there is a time of which the appointment occurs, the doctor that the appointment is with,
    the patient that the appointment is with, the nurse which the appointment is with (but this is rarely used),
    and the location of the appointment
    """
    time = models.DateTimeField()

    doctor = models.ForeignKey(to=Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE)
    nurse = models.ForeignKey(to=Nurse, on_delete=models.SET_NULL, null=True)

    location = models.ForeignKey(to=Hospital, on_delete=models.CASCADE)

    def __str__(self):
        time_str = self.time.strftime("%a %x at %X")
        return "%s with Dr. %s, %s, at %s" % (str(self.patient), str(self.doctor), str(self.location), time_str)

    def is_future(self):
        return self.time >= datetime.now()

    def is_today(self):
        now = datetime.now()
        return self.time.date() == now.date()

class Note(models.Model):
    """
    A note object which consists of the author, timestamp of when it was created, the content as a text field,
    and images allowed in
    """
    author = models.TextField()
    timestamp = models.DateTimeField()
    content = models.TextField()
    images = SeparatedValuesField()


class MedicalData(models.Model):
    """
    The medical data object which belongs to one patient, it contains the patient nd the notes.
    The creation of this is like the doctor uploading a test
    """
    patient = models.ForeignKey(to=Patient, related_name='medical_info', on_delete=models.SET_NULL, null=True)
    notes = models.ManyToManyField(Note, related_name='%(app_label)s_%(class)s_medical_notes')

    objects = InheritanceManager()


class MedicalTest(MedicalData):
    """
    The medical test object which will include the timestamp of when the medical test is released,
    the comments as a Note object and the sign off user which is the doctor that releasing the test
    """
    timestamp = models.DateTimeField()
    results = models.OneToOneField(to=Note, related_name='test_note', on_delete=models.SET_NULL, null=True)
    sign_off_user = models.ForeignKey(to=Doctor, on_delete=models.SET_NULL, null=True)


class MedicalHistory(MedicalData):
    """
    Medical History consists of the admission detail of a patient
    """
    admission_details = models.OneToOneField(to=AdmissionInfo, on_delete=models.CASCADE)


class Contact(models.Model):
    """
    A contact object which contains the user, name, primary phone number, and email
    """
    contact_user = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    contact_name = models.TextField()
    contact_primary = PhoneNumberField()
    contact_email = models.EmailField()

    objects = InheritanceManager()

    def __str__(self):
        return "%s : %s : %s" % (str(self.contact_user) if self.contact_name else self.contact_name, self.contact_email,
                                 self.contact_primary)


class PatientContact(Contact):
    """
    The emergency contact of a patient which extends Contact
    """
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE)
    relationship = models.IntegerField(choices=Relationship.choices(), default=Relationship.OTHER)
    contact_secondary = PhoneNumberField(blank=True)

    def __str__(self):
        contact_super = super(PatientContact, self).__str__()
        return "%s <-> %s" % (str(self.patient), contact_super)


### Message Models
class Message(models.Model):
    """
    Data container for a message consisting simply of a Sender, Receiver and Content
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    receiver = models.ForeignKey(to=User, related_name='receiver', on_delete=models.CASCADE)
    sender = models.ForeignKey(to=User, related_name='sender', on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255, default="")
    date = models.DateTimeField(default=datetime.now, blank=True)
    content = models.TextField()


class Inbox(models.Model):
    """
    Represents a general container of
    """
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, null=True)
    num_messages = models.PositiveIntegerField(default=0)
    messages = models.ManyToManyField(Message, blank=True)
    contacts = models.ManyToManyField(Contact, blank=True)

    def __str__(self):
        return "%s's Inbox" % str(User.objects.get_subclass(pk=self.user.pk))


@receiver(post_save)
def init_user_inbox(sender, **kwargs):
    inst = kwargs.get('instance')

    if not issubclass(sender, User) or (hasattr(inst, 'inbox') and getattr(inst, 'inbox', None) is not None):
        return

    print('Creating inbox for', inst)
    Inbox.objects.create(user=inst)
