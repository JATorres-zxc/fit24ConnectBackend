from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from account.models import CustomUser
from .models import Notification
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_membership_expiry_notifications():
    try:
        today = timezone.now().date()
        expiry_threshold = today + timedelta(days=14)
        users_to_notify = CustomUser.objects.filter(membership_end_date=expiry_threshold)
        for user in users_to_notify:
            Notification.objects.get_or_create(
                user=user,
                title="Membership Expiry Reminder",
                message=f"Hi {user.full_name or user.email}, your membership will expire on {user.membership_end_date}. Please renew soon.",
            )
        logger.info(f"Sent expiry notifications to {users_to_notify.count()} users.")
    except Exception as e:
        logger.error(f"Error sending expiry notifications: {e}")
