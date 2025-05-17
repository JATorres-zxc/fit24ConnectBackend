from django.urls import path
from .views import *

urlpatterns = [
    path('qr-scan/', QRScanView.as_view(), name='qr-scan'),
    path('my-access-logs/', UserAccessLogsView.as_view(), name='user-access-logs'),
    path('scan/', QRScanView.as_view(), name='facility-scan'),
    path('logs/', UserAccessLogsView.as_view(), name='user-access-logs'),
    path('reports/user-history/', UserAccessHistoryView.as_view(), name='user-access-history'),
]
