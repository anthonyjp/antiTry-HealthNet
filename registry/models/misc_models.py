from django.db import models

from localflavor.us.us_states import STATE_CHOICES

from registry.utility.models import Dictionary, SeparatedValuesField, TimeRange

class Hospital(models.Model):
    """
    Represents a hospital with a location
    """

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=300)
    state = models.CharField(max_length=2, choices=STATE_CHOICES, blank=False, null=False)
    zipcode = models.CharField(max_length=10, blank=False, null=False)
    identifiers = models.ForeignKey(to=Dictionary, on_delete=models.SET(Dictionary.empty))

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


class Prescription(models.Model):
    drug = models.ForeignKey(to=Drug, on_delete=models.PROTECT)

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

