from localflavor.us import us_states
from django.db import models

from registry.utility.models import Dictionary

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female')
)

BLOOD_CHOICES = (
    ('A', 'A'),
    ('B', 'B'),
    ('AB', 'AB'),
    ('O', 'O')
)

INSURANCE_CHOICES = (
    ('Self Insured', 'Self Insured'),
    ('Blue Cross Blue Shield', 'Blue Cross Blue Shield'),
    ('Super Legit MI', 'Super Legit Medical Insurance'),
    ('Not Legit MI', 'Not Legit Medical Insurance')
)

class Hospital(models.Model):
    """
    Represents a hospital with a location
    """

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=300)
    state = models.CharField(max_length=2, choices=us_states.STATE_CHOICES, blank=False, null=False)
    zipcode = models.CharField(max_length=10, blank=False, null=False)
    identifiers = models.ForeignKey(to=Dictionary, on_delete=models.SET(Dictionary.empty))

    def get_location(self) -> str:
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

class User(models.Model):
    firstName = models.CharField(max_length=100)
    middleInitial = models.CharField(max_length=1)
    lastName = models.CharField(max_length=100)
    email = models.EmailField()
    dateOfBirth = models.DateField()

    curHospital = models.ForeignKey(to=Hospital, related_name='cur_hospital', on_delete=models.PROTECT, null=False)
    prefHospital = models.ForeignKey(to=Hospital, related_name='pref_hospital', on_delete=models.SET_NULL, null=True)

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=GENDER_CHOICES[0][0])
    password = models.CharField(max_length=50)
    securityAnswer = models.CharField(max_length=50)


class Patient(User):
    height = models.PositiveIntegerField()
    weight = models.PositiveIntegerField()

    bloodType = models.CharField(max_length=2, choices=BLOOD_CHOICES, default=BLOOD_CHOICES[0][0])
    insurance = models.CharField(max_length=40, choices=INSURANCE_CHOICES, default=INSURANCE_CHOICES[0][0])
