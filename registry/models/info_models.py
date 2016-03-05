from django.db import models
from localflavor.us.models import PhoneNumberField
from model_utils.managers import InheritanceManager

from registry.utility.options import Relationship
from .data_models import Hospital, Note
from .user_models import Doctor, Nurse, Patient, AdmissionInfo
from ..utility.models import SeparatedValuesField


class Appointment(models.Model):
    time = models.DateTimeField()

    doctor = models.ForeignKey(to=Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE)
    nurse = models.ForeignKey(to=Nurse, on_delete=models.SET_NULL, null=True)

    location = models.ForeignKey(to=Hospital, on_delete=models.CASCADE)


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
    admission_details = models.OneToOneField(to=AdmissionInfo, on_delete=models.CASCADE)


class Contact(models.Model):
    contact_name = models.TextField()
    contact_primary = PhoneNumberField()
    contact_email = models.EmailField()

    objects = InheritanceManager()


class PatientContact(Contact):
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE)
    relationship = models.IntegerField(choices=Relationship.choices(), default=Relationship.OTHER)
    contact_seconday = PhoneNumberField()