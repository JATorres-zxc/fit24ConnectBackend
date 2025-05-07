from django.db import models
from django.conf import settings

class Report(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50, choices=[
        ('facility', 'Facility'),
        ('user', 'User'),
        ('trainer', 'Trainer'),
        ('general', 'General'),
        ('membership', 'Membership'),
        ('access_logs', 'Access Logs')
    ])
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    facility = models.ForeignKey('facility.Facility', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title