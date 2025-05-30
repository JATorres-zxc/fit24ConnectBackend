from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import CustomUser, Trainer
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# --- REGISTRATION ---
class RegistrationSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    is_trainer = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'confirm_password', 'is_trainer']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        return data

    def create(self, validated_data):
        is_trainer = validated_data.pop('is_trainer', False)
        full_name = validated_data.pop('full_name')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=full_name,
            is_trainer=is_trainer,
            is_active=True if is_trainer else False,
            membership_start_date=None,
            membership_end_date=None,
        )
        return user

# --- SIMPLIFIED USER SERIALIZER FOR USE INSIDE TRAINER ---
class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name']

# --- TRAINER SERIALIZER ---
class TrainerSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)  # avoids circular reference

    class Meta:
        model = Trainer
        fields = ['id', 'user', 'experience', 'contact_no']

# --- FULL USER SERIALIZER WITH TRAINER PROFILE INCLUDED ---
class UserSerializer(serializers.ModelSerializer):
    trainer_profile = TrainerSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "is_trainer",
            "trainer_profile",
            "height",
            "weight",
            "age",
            "type_of_membership",
            "membership_start_date",
            "membership_end_date",
        ]

# --- LOGIN SERIALIZER ---
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError({"non_field_errors": ["Invalid credentials"]})

        # Skip activation and membership checks if user is a trainer
        if not user.is_trainer:
            if not user.is_active:
                if not user.membership_start_date or not user.membership_end_date:
                    raise serializers.ValidationError({
                        "non_field_errors": ["Your account is pending activation. Please contact admin."]
                    })
                raise serializers.ValidationError({
                    "non_field_errors": ["Your membership is not currently active. Please check your membership dates."]
                })

        return {
            "user": user,
            "tokens": self.get_tokens_for_user(user),
        }

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

# --- FORGOT PASSWORD SERIALIZER ---
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get('email')
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "No account found with this email address."})
        return data

class MembershipTypeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['type_of_membership']
    
    def validate_type_of_membership(self, value):
        if value not in ['tier1', 'tier2', 'tier3']:
            raise serializers.ValidationError("Invalid membership type. Must be tier1, tier2, or tier3")
        return value

class MembershipStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['membership_start_date', 'membership_end_date']
        extra_kwargs = {
            'membership_start_date': {'required': True},
            'membership_end_date': {'required': True},
        }

    def validate(self, data):
        start_date = data.get('membership_start_date')
        end_date = data.get('membership_end_date')

        if not start_date or not end_date:
            raise serializers.ValidationError("Both start and end dates are required.")

        if end_date < start_date:
            raise serializers.ValidationError("End date must be after start date.")

        return data

    def update(self, instance, validated_data):
        # Update the dates
        instance.membership_start_date = validated_data['membership_start_date']
        instance.membership_end_date = validated_data['membership_end_date']

        # This will automatically update is_active via the save() method
        instance.save()
        return instance
