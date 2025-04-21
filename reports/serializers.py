from rest_framework import serializers
from facility.models import Facility, AccessLog
from .models import Report

class FacilityReportSerializer(serializers.ModelSerializer):
    access_logs = serializers.SerializerMethodField()

    class Meta:
        model = Facility
        fields = ['id', 'name', 'required_tier', 'access_logs']

    def get_access_logs(self, facility):
        logs = AccessLog.objects.filter(facility=facility).select_related('user').order_by('-timestamp')
        return [
            {
                'user': log.user.full_name,
                'timestamp': log.timestamp,
                'status': log.status,
                'reason': log.reason
            }
            for log in logs
        ]

class ReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = Report
        fields = ['id', 'title', 'notes', 'created_at', 'created_by', 'created_by_name']
        read_only_fields = ['created_by', 'created_at']