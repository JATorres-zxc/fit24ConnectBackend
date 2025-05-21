import qrcode
import json
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
from django.conf import settings

class Facility(models.Model):
    name = models.CharField(max_length=255)
    required_tier = models.CharField(
        max_length=10,
        choices=[('tier1', 'Tier 1'), ('tier2', 'Tier 2'), ('tier3', 'Tier 3')]
    )
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def __str__(self):
        return self.name

    def generate_qr_code(self):
        """Generate a QR code for the facility and save it."""
        data = json.dumps({
            "id": self.id,
            "name": self.name,
            "required_tier": self.required_tier
        })

        qr = qrcode.make(data)

        # Save the QR code image
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        # Clean the facility name to be filename-safe
        safe_name = self.name.lower().replace(' ', '_')
        filename = f"{safe_name}_qr_facilityid_{self.id}.png"

        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        """Generate QR code only after the object is saved."""
        if not self.pk:  # Only run before the first save
            super().save(*args, **kwargs)
        self.generate_qr_code()
        super().save(update_fields=['qr_code'])  # Save only the QR code field


class AccessLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('success', 'Success'), ('failed', 'Failed')])
    reason = models.TextField(blank=True, null=True)
    user_tier_at_time = models.CharField(
        max_length=10,
        choices=[('tier1', 'Tier 1'), ('tier2', 'Tier 2'), ('tier3', 'Tier 3')],
        blank=True,
        null=True
    )  # Store user's tier when scanning
    scan_method = models.CharField(max_length=20, choices=[
        ('qr', 'QR Code'),
        ('nfc', 'NFC'),
        ('manual', 'Manual Entry'),
        ('admin', 'Admin Override')
    ], default='qr')
    location = models.CharField(max_length=255, blank=True, null=True)  # Optional: GPS coordinates if available

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['facility']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
        ]
