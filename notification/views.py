from rest_framework import viewsets, permissions, status
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.response import Response
from rest_framework.decorators import action


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user).order_by('-created_at')
        if self.request.query_params.get('unread') == 'true':
            queryset = queryset.filter(is_read=False)
        if category := self.request.query_params.get('category'):
            queryset = queryset.filter(category=category)
        return queryset
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})
    
    @action(detail=True, methods=['patch'], url_path='mark-as-read')
    def mark_as_read(self, request, pk=None):
        try:
            notification = self.get_queryset().get(pk=pk)
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if notification.is_read:
            return Response({"detail": "Notification already marked as read."}, status=status.HTTP_200_OK)

        notification.is_read = True
        notification.save()
        return Response(self.get_serializer(notification).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='mark-all-as-read')
    def mark_all_as_read(self, request):
        updated = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({"detail": f"{updated} notifications marked as read."}, status=200)
