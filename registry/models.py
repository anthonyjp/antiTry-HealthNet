import uuid

from annoying import fields
from django.contrib.auth.models import User as DjangoUser
from django.db import models

from localflavor.us.models import PhoneNumberField
from localflavor.us.us_states import STATE_CHOICES
from registry.utility.options import Relationship
from model_utils.managers import InheritanceManager

from registry.utility.options import BloodType, Gender, INSURANCE_CHOICES, AdmitOptions
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
    name = models.CharField(max_length=255)
    # The company name, can have multiple
    providers = SeparatedValuesField()
    # Multiple side effects separated by commas
    side_effects = SeparatedValuesField()
    msds_link = models.CharField(max_length=512, null=True)

    def __str__(self):
        return self.name


class Note(models.Model):
    author = models.TextField()
    timestamp = models.DateTimeField()
    content = models.TextField()
    images = SeparatedValuesField()


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
    cur_hospital = models.ForeignKey(to=Hospital, related_name='%(app_label)s_%(class)s_cur_hospital',
                                     on_delete=models.SET_NULL, null=True)

    gender = models.SmallIntegerField(choices=Gender.choices(), default=Gender.MALE)
    security_question = models.SmallIntegerField(choices=SecQ.choices(), default=SecQ.Q1)
    security_answer = models.CharField(max_length=50, null=False, blank=False)

    objects = InheritanceManager()

    def __str__(self):
        if self.middle_initial:
            return "%s %s. %s" % (self.first_name, self.middle_initial, self.last_name)
        else:
            return "%s %s" % (self.first_name, self.last_name)


class Doctor(User):
    hospitals = models.ManyToManyField(Hospital, related_name='provider_to')

class Nurse(User):
    hospital = models.ForeignKey(Hospital)


class Patient(User):
    height = models.PositiveIntegerField()
    weight = models.PositiveIntegerField()

    provider = models.ForeignKey(to=Doctor, related_name='providers', on_delete=models.SET_NULL, null=True)
    #admission_status = models.OneToOneField(to=AdmissionInfo, related_name='patient_status', on_delete=models.SET_NULL,
    #                                        null=True)
    admission_status = models.BooleanField(default=False)
    pref_hospital = models.ForeignKey(to=Hospital, related_name='%(app_label)s_%(class)s_pref_hospital',
                                      on_delete=models.SET_NULL, null=True)

    blood_type = models.SmallIntegerField(choices=BloodType.choices(), default=BloodType.UNKNOWN)
    insurance = models.CharField(max_length=40, choices=INSURANCE_CHOICES, default=INSURANCE_CHOICES[0][0])
    transfer_request = models.BooleanField(default=False)

class Administrator(User):
    is_sysadmin = models.BooleanField(default=False)

class Admittance(models.Model):
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE)
    admitted_by = models.ForeignKey(to=User, on_delete=models.SET_NULL, related_name='admitted_by', null=True)
    hospital = models.ForeignKey(Hospital)
    reason = models.SmallIntegerField(choices=AdmitOptions.choices(), default=AdmitOptions.EMERGENCY)
    admission_time = models.OneToOneField(to=TimeRange, on_delete=models.SET_NULL, null=True)
    request = models.BooleanField(default=False)
    def __str__(self):
        return "%s was admitted by %s to %s on %s" % \
               (self.patient, self.admitted_by, self.hospital, self.admission_time.start_time)


class Prescription(models.Model):
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

    def can_refill(self):
        return self.refills > 0

    def refill(self):
        if not self.can_refill():
            raise RuntimeError('Cannot refill')
        else:
            self.refills -= 1
            return self.refills


### Patient Data Models

class Appointment(models.Model):
    time = models.DateTimeField()

    doctor = models.ForeignKey(to=Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE)
    nurse = models.ForeignKey(to=Nurse, on_delete=models.SET_NULL, null=True)

    location = models.ForeignKey(to=Hospital, on_delete=models.CASCADE)

    def __str__(self):
        time_str = self.time.strftime("%a %x at %X")
        return "%s with Dr. %s, %s, at %s" % (str(self.patient), str(self.doctor), str(self.location), time_str)


class MedicalData(models.Model):
    patient = models.ForeignKey(to=Patient, related_name='medical_info', on_delete=models.SET_NULL, null=True)

    patient_name = models.TextField()
    doctor = models.TextField()
    sign_off = models.TextField()
    notes = models.ManyToManyField(Note, related_name='%(app_label)s_%(class)s_medical_notes')

    objects = InheritanceManager()


class MedicalTest(MedicalData):
    timestamp = models.DateTimeField()
    results = models.OneToOneField(to=Note, related_name='test_note', on_delete=models.SET_NULL, null=True)
    images = SeparatedValuesField()
    sign_off_user = models.ForeignKey(to=Doctor, on_delete=models.SET_NULL, null=True)


class MedicalHistory(MedicalData):
    admission_details = models.OneToOneField(to=Admittance, on_delete=models.CASCADE)


class Contact(models.Model):
    contact_user = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    contact_name = models.TextField()
    contact_primary = PhoneNumberField()
    contact_email = models.EmailField()

    objects = InheritanceManager()

    def __str__(self):
        return "%s : %s : %s" % (str(self.contact_user) if self.contact_name else self.contact_name, self.contact_email,
                                 self.contact_primary)


class PatientContact(Contact):
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
    uuid = models.UUIDField(primary_key=True)
    receiver = models.ForeignKey(to=User, related_name='receiver', on_delete=models.CASCADE)
    sender = models.ForeignKey(to=User, related_name='sender', on_delete=models.SET_NULL, null=True)
    content = models.TextField()


class Inbox(models.Model):
    """
    Represents a general container of
    """
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, null=True)
    num_messages = models.PositiveIntegerField(default=0)
    messages = models.ManyToManyField(Message)
    contacts = models.ManyToManyField(Contact)

    def __str__(self):
        return "%s's Inbox" % str(User.objects.get_subclass(pk=self.user.pk))
