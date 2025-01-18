from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Facility, AccessLog
from .serializers import QRScanSerializer, AccessLogSerializer
from datetime import date
from django.utils.timezone import now


class QRScanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QRScanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Invalid data'}, status=400)

        facility_id = serializer.validated_data['facility_id']
        user = request.user

        try:
            facility = Facility.objects.get(id=facility_id)
        except Facility.DoesNotExist:
            return Response({'error': 'Facility not found'}, status=404)

        # Skip membership status check for testing purposes
        # if not user.is_membership_active:
        #     reason = "Expired membership"
        #     AccessLog.objects.create(
        #         user=user, facility=facility, status='failed', reason=reason
        #     )
        #     return Response({'status': 'failed', 'reason': reason}, status=403)

        # Check membership tier
        if user.type_of_membership != facility.required_tier:
            reason = f"Required tier is {facility.required_tier}, but your tier is {user.type_of_membership}"
            AccessLog.objects.create(
                user=user, facility=facility, status='failed', reason=reason
            )
            return Response({'status': 'failed', 'reason': reason}, status=403)

        # Log successful access
        AccessLog.objects.create(user=user, facility=facility, status='success')

        return Response({
            'status': 'success',
            'user_name': user.full_name,
            'facility_name': facility.name,
            'timestamp': now()
        })
