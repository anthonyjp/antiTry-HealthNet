import datetime

from django.db import models
from django.utils import timezone

"""
Default timeRange
For use in viewing system statistics and system logs
For use in viewing prescriptions
For use in viewing appointments
start_time is necessary
end_time is not necessary (can be null)
"""
class TimeRange(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)

    def extend(self, hours):
        self.end_time += datetime.timedelta(hours=hours)
        self.save()

    def duration(self):
        return self.end_time - self.start_time

    def is_elapsed(self):
        return self.end_time and timezone.now() > self.end_time

    def in_range(self, dt):
        assert(isinstance(dt, datetime.datetime))
        return self.start_time <= dt <= self.end_time

class Dictionary(models.Model):
    """
    A specialized Dictionary datastore that is backed by KeyValue models. These can ONLY store Key-Value string pairs
    and with that the key must be within 100 characters.
    """

    name = models.CharField(max_length=100)

    def put(self, key, value):
        if self.get(key):
            kv = self.keyvalue_set.get(pk=key)
            kv.value = value
            kv.save()
        else:
            self.keyvalue_set.create(key=key, value=value)

    def get(self, key):
        try:
            return self.keyvalue_set.get(pk=key)
        except models.ObjectDoesNotExist:
            return None

    @staticmethod
    def empty():
        return Dictionary.objects.create()


class KeyValue(models.Model):
    dict = models.ForeignKey(to=Dictionary, on_delete=models.CASCADE)
    key = models.CharField(max_length=100, primary_key=True)
    value = models.TextField()


class SeparatedValuesField(models.TextField):
    """
    A specialized field for storing iterable types, specifically Tuple and List. The backing database field is a
    TextField and the values are converted to string using either the implementation defined by __repr__ (using the
    repr() builtin) or using a user-defined representation function. Note that the function is used on all objects in
    the iterable.

    On getting the value for the database it is split again and returned as a list of strings created from either repr
    or the user-defined function specified earlier.
    """

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
        self.py_to_str = kwargs.pop('converter', repr)
        super(SeparatedValuesField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return

        if isinstance(value, list):
            return value

        return value.split(self.token)

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if not value:
            return
        assert(isinstance(value, list) or isinstance(value, tuple))
        return self.token.join([self.py_to_str(s) for s in value])

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
