from rest_framework import serializers
from .models import Facility, AccessLog
from django.utils.timezone import now

class QRScanSerializer(serializers.Serializer):
    facility_id = serializers.IntegerField()  # Pass facility ID with the QR scan data

class AccessLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    facility_name = serializers.CharField(source='facility.name', read_only=True)
    facility_required_tier = serializers.CharField(source='facility.required_tier', read_only=True)
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = AccessLog
        fields = [
            'id',
            'user_name',
            'user_email',
            'facility_name',
            'facility_required_tier',
            'user_tier_at_time',
            'timestamp', 
            'status', 
            'reason',
            'scan_method',
            'location'
        ]
