from django.urls import path
from .views import (
    ReportListCreateView,
    ReportRetrieveUpdateDestroyView,
    GenerateFacilityPDFReport,
)

urlpatterns = [
    path('', ReportListCreateView.as_view(), name='report-list-create'),
    path('<int:pk>/', ReportRetrieveUpdateDestroyView.as_view(), name='report-detail'),
    path('facility-access-pdf/', GenerateFacilityPDFReport.as_view(), name='facility-access-pdf'),
]
