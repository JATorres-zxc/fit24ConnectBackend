from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Facility

class FacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'required_tier', 'qr_code_display')
    readonly_fields = ('qr_code_display',)

    def qr_code_display(self, obj):
        """Display QR code in the admin panel."""
        if obj.qr_code:
            return mark_safe(f'<img src="{obj.qr_code.url}" width="100" height="100" />')
        return "No QR Code"

    qr_code_display.short_description = "QR Code"

admin.site.register(Facility, FacilityAdmin)
