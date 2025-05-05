from rest_framework import serializers
from account.models import CustomUser

class ProfileSerializer(serializers.ModelSerializer):
    membership_status = serializers.SerializerMethodField()
    experience = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = [
            'email', 'full_name', 'contact_number', 'messenger_account', 'complete_address',
            'nationality', 'birthdate', 'gender',
            'height', 'weight', 'age',
            'type_of_membership', 'membership_status', 'experience'
        ]

    def get_membership_status(self, obj):
        return "Active" if obj.is_membership_active else "Inactive"

    def to_representation(self, instance):
        # Overrides get_experience logic during serialization
        data = super().to_representation(instance)
        if instance.is_trainer and hasattr(instance, 'trainer_profile'):
            data['experience'] = instance.trainer_profile.experience
        else:
            data['experience'] = None
        return data

    #  (PATCH) for both email and trainer_profile.experience
    def update(self, instance, validated_data):
        # Update fields from CustomUser
        experience = validated_data.pop('experience', None)
        email = validated_data.get('email')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle experience separately for trainer
        if instance.is_trainer and hasattr(instance, 'trainer_profile') and experience is not None:
            instance.trainer_profile.experience = experience
            instance.trainer_profile.save()

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)