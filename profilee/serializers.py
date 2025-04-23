from rest_framework import serializers
from account.models import CustomUser

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'full_name', 'contact_number', 'messenger_account', 'complete_address',
            'nationality', 'birthdate', 'gender',
            'height', 'weight', 'age'
        ]
