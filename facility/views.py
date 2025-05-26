from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import generics
from .models import Facility, AccessLog
from .serializers import QRScanSerializer, AccessLogSerializer
from datetime import date
from django.utils.timezone import now
import json
from django.utils import timezone

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
            qr_data = json.loads(qr_code_data)
            facility_uuid = qr_data.get("uuid")
            if not facility_uuid:
                raise ValueError("Missing UUID")
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            return Response({'error': 'Invalid QR code format'}, status=400)

        user = request.user

        # Validate facility existence
        try:
            facility = Facility.objects.get(uuid=facility_uuid)
        except Facility.DoesNotExist:
            return Response({'error': 'Facility not found'}, status=404)

        # ✅ Trainer override: allow access regardless of membership
        if user.is_trainer:
            AccessLog.objects.create(
                user=user,
                facility=facility,
                status='success',
                user_tier_at_time='trainer',
                scan_method=scan_method,
                location=location
            )
            return Response({
                'status': 'success',
                'user_name': user.full_name,
                'user_tier': 'trainer',
                'facility_name': facility.name,
                'facility_tier': facility.required_tier,
                'timestamp': timezone.localtime(timezone.now()).isoformat(),
                'access_granted': True,
                'message': 'Access granted (Trainer)'
            })

        # Check if user's membership is active
        if not user.is_membership_active:
            reason = "Inactive membership"
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
                'message': 'Access denied. Your membership is inactive. Please renew your membership.'
            }, status=403)

        # Check tier access
        user_tier = user.type_of_membership
        required_tier = facility.required_tier

        # Define tier hierarchy
        tier_hierarchy = {
            'tier1': 1,
            'tier2': 2,
            'tier3': 3
        }

        # Check if user's tier is at least as high as required tier
        if tier_hierarchy[user_tier] < tier_hierarchy[required_tier]:
            reason = f"Required tier is {required_tier}, but your tier is {user_tier}"
            AccessLog.objects.create(
                user=user,
                facility=facility,
                status='failed',
                reason=reason,
                user_tier_at_time=user_tier,
                scan_method=scan_method,
                location=location
            )
            return Response({
                'status': 'failed',
                'reason': reason,
                'required_tier': required_tier,
                'user_tier': user_tier,
                'message': 'Access denied. Admins have been notified.'
            }, status=403)

        # Log successful access
        AccessLog.objects.create(
            user=user,
            facility=facility,
            status='success',
            user_tier_at_time=user_tier,
            scan_method=scan_method,
            location=location
        )

        return Response({
            'status': 'success',
            'user_name': user.full_name,
            'user_tier': user_tier,
            'facility_name': facility.name,
            'facility_tier': required_tier,
            'timestamp': timezone.now().isoformat(),
            'access_granted': True
        })

class UserAccessLogsView(generics.ListAPIView):
    serializer_class = AccessLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only the current user's access logs
        return AccessLog.objects.filter(user=self.request.user).order_by('-timestamp')

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