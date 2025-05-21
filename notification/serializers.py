from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    
    def get_created_at(self, obj):
        return obj.created_at.strftime("%b %d, %Y %H:%M")
    
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'created_at', 'is_read', 'category']
        read_only_fields = ['id', 'title', 'message', 'created_at', 'category']
