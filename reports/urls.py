from django.urls import path
from .views import *

urlpatterns = [
    path('reports/', ReportListCreateView.as_view(), name='report-list-create'),
    path('reports/<int:pk>/', ReportRetrieveUpdateDestroyView.as_view(), name='report-detail'),
    path('reports/generate/', GenerateReportView.as_view(), name='generate-report'),
    path('reports/summary/', FacilityAccessSummaryView.as_view(), name='facility-access-summary'),
    path('reports/user-history/', UserAccessHistoryView.as_view(), name='user-access-history'),
]
