from rest_framework import serializers
from facility.models import Facility, AccessLog
from .models import Report
from account.models import CustomUser

class FacilityReportSerializer(serializers.ModelSerializer):
    access_logs = serializers.SerializerMethodField()

    class Meta:
        model = Facility
        fields = ['id', 'name', 'required_tier', 'access_logs']

    def get_access_logs(self, facility):
        request = self.context.get('request')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        logs = AccessLog.objects.filter(facility=facility).select_related('user')

        if start_date:
            logs = logs.filter(timestamp__date__gte=start_date)
        if end_date:
            logs = logs.filter(timestamp__date__lte=end_date)

        logs = logs.order_by('-timestamp')

        return [
            {
                'user': log.user.full_name,
                'timestamp': log.timestamp,
                'status': log.status,
                'reason': log.reason
            }
            for log in logs
        ]

class MembershipReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'email', 'type_of_membership', 'is_active', 'membership_start_date', 'membership_end_date']

class ReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    facility_name = serializers.CharField(source='facility.name', read_only=True)

    class Meta:
        model = Report
        fields = ['id', 'title', 'type', 'notes', 'created_at', 'created_by', 'created_by_name', 'start_date', 'end_date', 'facility', 'facility_name']
        read_only_fields = ['created_by', 'created_at']