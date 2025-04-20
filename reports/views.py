from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUser
from facility.models import Facility, AccessLog
from rest_framework import generics, permissions
from .models import Report
from .serializers import ReportSerializer

# class GenerateFacilityPDFReport(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         facilities = Facility.objects.all().order_by('id')
#         data = []

#         for facility in facilities:
#             logs = AccessLog.objects.filter(facility=facility).select_related('user').order_by('-timestamp')
#             data.append({
#                 'facility': facility,
#                 'logs': logs
#             })

#         html = render_to_string('reports/facility_report_template.html', {'data': data})
#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename="facility_report.pdf"'
#         pisa_status = pisa.CreatePDF(html, dest=response)

#         if pisa_status.err:
#             return HttpResponse('Error generating PDF', status=500)
#         return response


class GenerateFacilityPDFReport(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        # Use test data from request body if provided, otherwise pull from DB
        mock_data = [
            {
                "facility": {
                    "name": "Main Gym",
                    "required_tier": "tier1"
                },
                "logs": [
                    {
                        "user": {
                            "full_name": "Alice Johnson",
                            "email": "alice@example.com",
                            "type_of_membership": "tier1",
                            "username": "alicej"
                        },
                        "timestamp": "2025-04-05T10:00:00Z",
                        "status": "success",
                        "reason": ""
                    },
                    {
                        "user": {
                            "full_name": "Bob Smith",
                            "email": "bob@example.com",
                            "type_of_membership": "tier2",
                            "username": "bobsmith"
                        },
                        "timestamp": "2025-04-05T12:30:00Z",
                        "status": "failed",
                        "reason": "Membership tier too low"
                    }
                ]
            },
            {
                "facility": {
                    "name": "Swimming Pool",
                    "required_tier": "tier2"
                },
                "logs": []
            }
        ]

        # Now use mock_data to generate the report as shown above

        if mock_data:
            data = []
            for facility in mock_data:
                data.append({
                    'facility': {
                        'name': facility.get('name'),
                        'required_tier': facility.get('required_tier')
                    },
                    'logs': facility.get('logs', [])
                })
        else:
            facilities = Facility.objects.all().order_by('id')
            data = []

            for facility in facilities:
                logs = AccessLog.objects.filter(facility=facility).select_related('user').order_by('-timestamp')
                data.append({
                    'facility': facility,
                    'logs': logs
                })
        
        # Debug: Print the data being passed to the template
        print(data)

        html = render_to_string('reports/facility_report_template.html', {'data': data})
        
        # Debug: Print the rendered HTML
        print(html)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="facility_report.pdf"'
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