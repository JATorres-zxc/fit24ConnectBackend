from django.urls import path
from .views import QRScanView

urlpatterns = [
    path('qr-scan/', QRScanView.as_view(), name='qr-scan'),
]
