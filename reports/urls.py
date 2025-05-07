from django.urls import path
from .views import GenerateReportView, ReportListCreateView, ReportRetrieveUpdateDestroyView

urlpatterns = [
    path('reports/', ReportListCreateView.as_view(), name='report-list-create'),
    path('reports/<int:pk>/', ReportRetrieveUpdateDestroyView.as_view(), name='report-detail'),
    path('reports/generate/', GenerateReportView.as_view(), name='generate-report'),
]
