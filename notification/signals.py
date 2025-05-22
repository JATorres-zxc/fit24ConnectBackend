from django.db.models.signals import post_save
from django.dispatch import receiver
from account.models import CustomUser
from .models import Notification
from facility.models import AccessLog

@receiver(post_save, sender=CustomUser)
def notify_new_user(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance,
            title="Welcome!",
            message="Thanks for joining! Let us know if you need help getting started.",
        )

@receiver(post_save, sender=AccessLog)
def notify_failed_access(sender, instance, created, **kwargs):
    if created and instance.status == 'failed':
        # Use values_list for more efficient query
        admin_ids = CustomUser.objects.filter(is_admin=True).values_list('id', flat=True)
        
        # Bulk create notifications
        notifications = [
            Notification(
                user_id=admin_id,
                title="Unauthorized Access Attempt",
                # message=f"User {instance.user.email} (Tier: {instance.user_tier_at_time}) "
                #         f"attempted to access {instance.facility.name} (Required Tier: {instance.facility.required_tier}). "
                #         f"Reason: {instance.reason}",
                message = f"{instance.user.full_name} ({instance.user.email}) attempted to access {instance.facility.name} without the required tier.",
                category='security'
            )
            for admin_id in admin_ids
        ]
        Notification.objects.bulk_create(notifications)