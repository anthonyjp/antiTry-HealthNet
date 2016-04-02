from django.db import models

from .user_models import User
from .info_models import Contact
from django.db.models.signals import post_save
from django.dispatch import receiver



class Message(models.Model):
    """
    Data container for a message consisting simply of a Sender, Receiver and Content
    """
    uuid = models.UUIDField(primary_key=True)
    receiver = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='message_receiver')
    sender = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True, related_name='message_sender')
    content = models.TextField()

class Inbox(models.Model):
    """
    Represents a general container for User messages
    """
    num_messages = models.PositiveIntegerField(default=0)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    messages = models.ManyToManyField(Message)
    contacts = models.ManyToManyField(Contact)

@receiver(post_save, sender=User)
def _init_user_inbox(self, sender, instance, created, **kwargs):
    print("In Method")
    if created:
        print("In If Statement")
        inbox = Inbox(user=sender)
        inbox.save()