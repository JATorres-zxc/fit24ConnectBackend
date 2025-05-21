from rest_framework import serializers
from account.models import CustomUser

class ProfileSerializer(serializers.ModelSerializer):
    membership_status = serializers.SerializerMethodField()
    experience = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True
    )

    class Meta:
        model = CustomUser
        fields = [
            'email', 'full_name', 'contact_number', 'complete_address',
            'height', 'weight', 'age',
            'type_of_membership', 'membership_status',
            'experience'
        ]
        extra_kwargs = {
            'email': {'read_only': True}
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_trainer = self.context.get('is_trainer', False)
        self.fields['experience'].write_only = not is_trainer

    def get_membership_status(self, obj):
        return "Active" if obj.is_membership_active else "Inactive"

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.is_trainer:
            trainer_profile = instance.ensure_trainer_profile
            data['experience'] = trainer_profile.experience if trainer_profile else None
        else:
            if 'experience' in data:
                data.pop('experience')
            
        return data

    def update(self, instance, validated_data):
        experience = validated_data.pop('experience', None)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle experience for trainer
        if instance.is_trainer and experience is not None:
            trainer_profile = instance.ensure_trainer_profile
            trainer_profile.experience = experience
            trainer_profile.save()

        return instance

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)