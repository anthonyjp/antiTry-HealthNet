from django.db import models

from localflavor.us.us_states import STATE_CHOICES

from registry.utility.models import Dictionary, SeparatedValuesField

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


class Drug(models.Model):
    name = models.CharField(max_length=255)
    providers = SeparatedValuesField()
    side_effects = SeparatedValuesField()
    msdsLink = models.CharField(max_length=512)


class Note(models.Model):
    author = models.TextField()
    timestamp = models.DateTimeField()
    content = models.TextField()
    images = SeparatedValuesField()