from django.db import models

from django.contrib.auth.models import User as DjangoUser
from model_utils.managers import InheritanceManager

from .options import BloodType, Gender, INSURANCE_CHOICES
from .data_models import Hospital, Drug
from ..utility.models import TimeRange, Dictionary


class User(DjangoUser):
    uuid = models.UUIDField(primary_key=True)
    middle_initial = models.CharField(max_length=1)
    date_of_birth = models.DateField()

    cur_hospital = models.ForeignKey(to=Hospital, related_name='%(app_label)s_%(class)s_cur_hospital',
                                     on_delete=models.PROTECT, null=True)

    gender = models.CharField(max_length=1, choices=Gender.choices(), default=Gender.label(Gender.MALE))
    security_answer = models.CharField(max_length=50)

    objects = InheritanceManager()


class Doctor(User):
    hospitals = models.ManyToManyField(Hospital, related_name='provider_to')


class AdmissionInfo(models.Model):
    patient = models.TextField()
    admitted_by = models.TextField()

    doctors = models.ManyToManyField(Doctor)

    admission_time = models.OneToOneField(to=TimeRange, on_delete=models.PROTECT)
    prescriptions = models.OneToOneField(to=Dictionary, on_delete=models.PROTECT)


class Nurse(User):
    hospital = models.ForeignKey(Hospital)


class Patient(User):
    height = models.PositiveIntegerField()
    weight = models.PositiveIntegerField()

    admission_status = models.OneToOneField(to=AdmissionInfo, related_name='patient_status', on_delete=models.SET_NULL,
                                            null=True)
    pref_hospital = models.ForeignKey(to=Hospital, related_name='%(app_label)s_%(class)s_pref_hospital',
                                      on_delete=models.SET_NULL, null=True)

    blood_type = models.CharField(max_length=2, choices=BloodType.choices(), default=BloodType.label(BloodType.O))
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

