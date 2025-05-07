from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUser
from facility.models import Facility, AccessLog
from rest_framework import generics, permissions
from .models import Report
from .serializers import ReportSerializer, FacilityReportSerializer, MembershipReportSerializer, AccessLogSerializer
from account.models import CustomUser
from datetime import datetime
from rest_framework.response import Response
from django.db.models import Count, Q, models

class GenerateReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        report_type = request.query_params.get('type')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        facility_id = request.query_params.get('facility_id')

        if report_type == 'membership':
            return self.generate_membership_report(start_date, end_date)
        elif report_type == 'access_logs':
            return self.generate_access_logs_report(start_date, end_date, facility_id)
        else:
            return Response({'error': 'Invalid report type'}, status=400)

    def generate_membership_report(self, start_date, end_date):
        users = CustomUser.objects.all().order_by('-date_joined')

        if start_date:
            users = users.filter(date_joined__date__gte=start_date)
        if end_date:
            users = users.filter(date_joined__date__lte=end_date)

        active_users = users.filter(is_active=True)
        inactive_users = users.filter(is_active=False)

        serializer = MembershipReportSerializer(users, many=True)

        html = render_to_string('reports/membership_report_template.html', {
            'active_users': active_users,
            'inactive_users': inactive_users,
            'start_date': start_date,
            'end_date': end_date
        })

        return self.generate_pdf_response(html, 'membership_report.pdf')

    def generate_access_logs_report(self, start_date, end_date, facility_id):
        facilities = Facility.objects.all()
        if facility_id:
            facilities = facilities.filter(id=facility_id)

        # Get summary statistics for the report
        summary = {
            'total_scans': 0,
            'success_scans': 0,
            'failed_scans': 0,
            'facilities': []
        }

        data = []
        for facility in facilities:
            logs = AccessLog.objects.filter(facility=facility).select_related('user')

            if start_date:
                logs = logs.filter(timestamp__date__gte=start_date)
            if end_date:
                logs = logs.filter(timestamp__date__lte=end_date)

            logs = logs.order_by('-timestamp')
            
            # Calculate stats for this facility
            facility_stats = {
                'id': facility.id,
                'name': facility.name,
                'required_tier': facility.required_tier,
                'total_scans': logs.count(),
                'success_scans': logs.filter(status='success').count(),
                'failed_scans': logs.filter(status='failed').count(),
                'scan_methods': list(logs.values('scan_method').annotate(count=Count('id')))
            }
            
            summary['total_scans'] += facility_stats['total_scans']
            summary['success_scans'] += facility_stats['success_scans']
            summary['failed_scans'] += facility_stats['failed_scans']
            summary['facilities'].append(facility_stats)
            
            data.append({
                'facility': facility,
                'logs': logs[:100],  # Limit to 100 most recent for detailed view
                'stats': facility_stats
            })

        html = render_to_string('reports/access_logs_report_template.html', {
            'data': data,
            'summary': summary,
            'start_date': start_date,
            'end_date': end_date,
            'facility': facility if facility_id else None
        })

        filename = f"access_logs_report_{start_date}_to_{end_date}.pdf" if start_date and end_date else 'access_logs_report.pdf'
        return self.generate_pdf_response(html, filename)

    def generate_pdf_response(self, html, filename):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return HttpResponse(f'Error generating PDF: {pisa_status.err}', status=500)
        return response

class ReportListCreateView(generics.ListCreateAPIView):
    queryset = Report.objects.all().order_by('-created_at')
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ReportRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

class FacilityAccessSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        facility_id = request.query_params.get('facility_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        logs = AccessLog.objects.all()
        
        if facility_id:
            logs = logs.filter(facility_id=facility_id)
        if start_date:
            logs = logs.filter(timestamp__date__gte=start_date)
        if end_date:
            logs = logs.filter(timestamp__date__lte=end_date)
            
        # Get summary statistics
        total_scans = logs.count()
        success_scans = logs.filter(status='success').count()
        failed_scans = logs.filter(status='failed').count()
        
        # Group by user tier
        tier_stats = logs.values('user_tier_at_time').annotate(
            total=Count('id'),
            success=Count('id', filter=models.Q(status='success')),
            failed=Count('id', filter=models.Q(status='failed'))
        )
        
        # Group by scan method
        method_stats = logs.values('scan_method').annotate(
            total=Count('id'),
            success=Count('id', filter=models.Q(status='success')),
            failed=Count('id', filter=models.Q(status='failed'))
        )
        
        return Response({
            'total_scans': total_scans,
            'success_scans': success_scans,
            'failed_scans': failed_scans,
            'success_rate': (success_scans / total_scans * 100) if total_scans > 0 else 0,
            'tier_stats': tier_stats,
            'method_stats': method_stats,
            'time_period': {
                'start': start_date,
                'end': end_date
            }
        })

class UserAccessHistoryView(generics.ListAPIView):
    serializer_class = AccessLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        queryset = AccessLog.objects.all().select_related('user', 'facility')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)
            
        return queryset.order_by('-timestamp')