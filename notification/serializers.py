from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'created_at', 'is_read', 'category']
        read_only_fields = ['id', 'title', 'message', 'created_at']
