import uuid

from django.contrib.auth.models import User as DjangoUser
from django.db import models
from model_utils.managers import InheritanceManager

from registry.utility.options import BloodType, Gender, INSURANCE_CHOICES
from registry.utility.options import SecurityQuestion as SecQ
from .data_models import Hospital, Drug
from ..utility.models import TimeRange, Dictionary


DjangoUser.USERNAME_FIELD = 'email'
DjangoUser.REQUIRED_FIELDS = ['username']
DjangoUser._meta.get_field('username')._unique = False
DjangoUser._meta.get_field('email')._unique = True

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


class AdmissionInfo(models.Model):
    patient = models.TextField()
    admitted_by = models.TextField()

    doctors = models.ManyToManyField(Doctor)

    admission_time = models.OneToOneField(to=TimeRange, on_delete=models.SET_NULL, null=True)
    prescriptions = models.OneToOneField(to=Dictionary, on_delete=models.PROTECT)


class Nurse(User):
    hospital = models.ForeignKey(Hospital)


class Patient(User):
    height = models.PositiveIntegerField()
    weight = models.PositiveIntegerField()

    provider = models.ForeignKey(to=Doctor, related_name='providers', on_delete=models.SET_NULL, null=True)
    admission_status = models.OneToOneField(to=AdmissionInfo, related_name='patient_status', on_delete=models.SET_NULL,
                                            null=True)
    pref_hospital = models.ForeignKey(to=Hospital, related_name='%(app_label)s_%(class)s_pref_hospital',
                                      on_delete=models.SET_NULL, null=True)

    blood_type = models.SmallIntegerField(choices=BloodType.choices(), default=BloodType.UNKNOWN)
    insurance = models.CharField(max_length=40, choices=INSURANCE_CHOICES, default=INSURANCE_CHOICES[0][0])


class Administrator(User):
    is_sysadmin = models.BooleanField(default=False)


class Prescription(models.Model):
    drug = models.ForeignKey(to=Drug, on_delete=models.PROTECT)

    patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True)
    doctor = models.ForeignKey(to=Doctor, on_delete=models.CASCADE)

    count = models.PositiveIntegerField()   # prescription count (usually pill count)
    amount = models.PositiveIntegerField()  # milligrams
    refills = models.PositiveIntegerField()

    time_range = models.OneToOneField(to=TimeRange, on_delete=models.PROTECT)

    def __str__(self):
        return "%s at %d dosage for %s" % (str(self.drug), self.amount, str(self.patient))

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

