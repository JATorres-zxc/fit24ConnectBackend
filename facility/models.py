from django.db import models
from django.conf import settings
from datetime import datetime

class Facility(models.Model):
    name = models.CharField(max_length=255)
    required_tier = models.CharField(
        max_length=10,
        choices=[('tier1', 'Tier 1'), ('tier2', 'Tier 2'), ('tier3', 'Tier 3')]
    )

    def __str__(self):
        return self.name


class AccessLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('success', 'Success'), ('failed', 'Failed')])
    reason = models.TextField(blank=True, null=True)  # Reason for failed access
