from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from account.models import CustomUser
from notification.models import Notification

class Command(BaseCommand):
    help = 'Notify users whose memberships expire in 14 days'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        expiry_threshold = today + timedelta(days=14)

        users_to_notify = CustomUser.objects.filter(
            membership_end_date=expiry_threshold
        )

        for user in users_to_notify:
            Notification.objects.get_or_create(
                user=user,
                title="Membership Expiry Reminder",
                message=f"Hi {user.full_name or user.email}, your membership will expire on {user.membership_end_date}. Please renew soon.",
            )
            self.stdout.write(f"Notification sent to {user.email}")
