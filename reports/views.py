from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUser
from facility.models import Facility, AccessLog
from rest_framework import generics, permissions
from .models import Report
from .serializers import ReportSerializer, FacilityReportSerializer, MembershipReportSerializer
from account.models import CustomUser
from datetime import datetime
from rest_framework.response import Response

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

        data = []
        for facility in facilities:
            logs = AccessLog.objects.filter(facility=facility).select_related('user')

            if start_date:
                logs = logs.filter(timestamp__date__gte=start_date)
            if end_date:
                logs = logs.filter(timestamp__date__lte=end_date)

            logs = logs.order_by('-timestamp')
            data.append({
                'facility': facility,
                'logs': logs
            })

        html = render_to_string('reports/access_logs_report_template.html', {
            'data': data,
            'start_date': start_date,
            'end_date': end_date,
            'facility': facility if facility_id else None
        })

        return self.generate_pdf_response(html, 'access_logs_report.pdf')

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