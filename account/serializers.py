from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import CustomUser
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'email', 'password', 'referral_code', 'full_name',
            'contact_number', 'messenger_account', 'complete_address',
            'nationality', 'birthdate', 'gender', 'type_of_membership'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        # Check for existing email
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        
        return data

    def create(self, validated_data):
        with transaction.atomic():
            # Create the user using create_user to ensure password hashing
            user = CustomUser.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                full_name=validated_data['full_name'],
                contact_number=validated_data['contact_number'],
                messenger_account=validated_data.get('messenger_account'),
                complete_address=validated_data['complete_address'],
                nationality=validated_data['nationality'],
                birthdate=validated_data['birthdate'],
                gender=validated_data['gender'],
                type_of_membership=validated_data['type_of_membership'],
                referral_code=validated_data.get('referral_code'),
            )
        
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("User account is inactive")

        return {
            "user": user,
            "tokens": self.get_tokens_for_user(user)
        }

    def get_tokens_for_user(self, user):
        """
        Generate and return refresh and access tokens for the user
        """
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get('email')
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "No account found with this email address."})
        return data

