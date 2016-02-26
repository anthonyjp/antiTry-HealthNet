from django.db import models

from .user_models import User
from .info_models import Contact


class Message(models.Model):
    """
    Data container for a message consisting simply of a Sender, Receiver and Content
    """
    uuid = models.UUIDField(primary_key=True)
    receiver = models.ForeignKey(to=User, on_delete=models.CASCADE)
    sender = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()


class Inbox(models.Model):
    """
    Represents a general container of
    """
    num_messages = models.PositiveIntegerField(default=0)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    messages = models.ManyToManyField(Message)
    contacts = models.ManyToManyField(Contact)

