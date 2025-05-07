from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import Facility, AccessLog
from .serializers import QRScanSerializer, AccessLogSerializer
from datetime import date
from django.utils.timezone import now
import json

class QRScanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Extract the raw QR code data
        qr_code_data = request.data.get("qrCode", None)
        scan_method = request.data.get("scan_method", "qr")
        location = request.data.get("location", None)

        if not qr_code_data:
            return Response({'error': 'QR Code data is missing'}, status=400)

        try:
            # Parse JSON string inside qrCode
            qr_data = json.loads(qr_code_data)
            facility_id = qr_data.get("id")  # Extract facility ID
        except (json.JSONDecodeError, KeyError, TypeError):
            return Response({'error': 'Invalid QR code format'}, status=400)

        user = request.user

        # Validate facility existence
        try:
            facility = Facility.objects.get(id=facility_id)
        except Facility.DoesNotExist:
            return Response({'error': 'Facility not found'}, status=404)

        # Check membership tier
        if user.type_of_membership != facility.required_tier:
            reason = f"Required tier is {facility.required_tier}, but your tier is {user.type_of_membership}"
            AccessLog.objects.create(
                user=user,
                facility=facility,
                status='failed',
                reason=reason,
                user_tier_at_time=user.type_of_membership,
                scan_method=scan_method,
                location=location
            )
            return Response({
                'status': 'failed',
                'reason': reason,
                'required_tier': facility.required_tier,
                'user_tier': user.type_of_membership
            }, status=403)

        # Log successful access
        AccessLog.objects.create(
            user=user,
            facility=facility,
            status='success',
            user_tier_at_time=user.type_of_membership,
            scan_method=scan_method,
            location=location
        )

        return Response({
            'status': 'success',
            'user_name': user.full_name,
            'user_tier': user.type_of_membership,
            'facility_name': facility.name,
            'facility_tier': facility.required_tier,
            'timestamp': now(),
            'access_granted': True
        })

class UserAccessLogsView(generics.ListAPIView):
    serializer_class = AccessLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only the current user's access logs
        return AccessLog.objects.filter(user=self.request.user).order_by('-timestamp')