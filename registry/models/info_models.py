from django.db import models
from localflavor.us.models import PhoneNumberField
from model_utils.managers import InheritanceManager
from registry.utility.options import Relationship
from .data_models import Hospital, Note
from .user_models import Doctor, Nurse, Patient, AdmissionInfo, User
from ..utility.models import SeparatedValuesField


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
    admission_details = models.OneToOneField(to=AdmissionInfo, on_delete=models.CASCADE)


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

