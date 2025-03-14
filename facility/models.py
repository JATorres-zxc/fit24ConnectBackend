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
        self.qr_code.save(f"facility_{self.id}.png", ContentFile(buffer.getvalue()), save=False)

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
    reason = models.TextField(blank=True, null=True)  # Reason for failed access
