from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Trainer

@receiver(post_save, sender=CustomUser)
def handle_trainer_status_change(sender, instance, **kwargs):
    if instance.is_trainer and not hasattr(instance, 'trainer_profile'):
        Trainer.objects.create(user=instance, experience="", contact_no="")
    elif not instance.is_trainer and hasattr(instance, 'trainer_profile'):
        instance.trainer_profile.delete()