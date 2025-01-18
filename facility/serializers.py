from rest_framework import serializers
from .models import Facility, AccessLog
from django.utils.timezone import now

class QRScanSerializer(serializers.Serializer):
    facility_id = serializers.IntegerField()  # Pass facility ID with the QR scan data

class AccessLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    facility_name = serializers.CharField(source='facility.name', read_only=True)

    class Meta:
        model = AccessLog
        fields = ['user_name', 'facility_name', 'timestamp', 'status', 'reason']
