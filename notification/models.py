from django.db import models
from django.conf import settings
from django.utils import timezone

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    metadata = models.JSONField(null=True, blank=True)
    CATEGORY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('system', 'System'),
        ('security', 'Security Alert'),  # New category for security-related notifications
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='info')
    
    def __str__(self):
        return f"Notification for {self.user.email} - {self.title}"
