from rest_framework import serializers
from account.models import CustomUser

class ProfileSerializer(serializers.ModelSerializer):
    membership_status = serializers.SerializerMethodField()
    experience = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'full_name', 'contact_number', 'messenger_account', 'complete_address',
            'nationality', 'birthdate', 'gender',
            'height', 'weight', 'age',
            'type_of_membership', 'membership_status', 'experience'
        ]

    def get_membership_status(self, obj):
        return "Active" if obj.is_membership_active else "Inactive"

    def get_experience(self, obj):
        if obj.is_trainer and hasattr(obj, 'trainer_profile'):
            return obj.trainer_profile.experience
        return None
