from django.db.models.signals import post_save
from django.dispatch import receiver
from account.models import CustomUser
from .models import Notification

@receiver(post_save, sender=CustomUser)
def notify_new_user(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance,
            title="Welcome!",
            message="Thanks for joining! Let us know if you need help getting started.",
        )
