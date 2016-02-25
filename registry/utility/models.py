from django.db import models


class Dictionary(models.Model):
    name = models.CharField(max_length=100)

    def empty(self):
        return Dictionary.objects.create()


class KeyValue(models.Model):
    dict = models.ForeignKey(to=Dictionary, on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    value = models.TextField()
