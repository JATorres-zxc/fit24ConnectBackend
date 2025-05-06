from django.urls import path
from .views import *

urlpatterns = [
    path('qr-scan/', QRScanView.as_view(), name='qr-scan'),
    path('my-access-logs/', UserAccessLogsView.as_view(), name='user-access-logs'),
]
