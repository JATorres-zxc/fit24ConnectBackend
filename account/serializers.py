from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import CustomUser, Trainer
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# --- REGISTRATION ---
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    is_trainer = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'is_trainer']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        return data

    def create(self, validated_data):
        is_trainer = validated_data.pop('is_trainer', False)
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            is_trainer=is_trainer
        )

        # Create Trainer profile if user is a trainer
        if is_trainer:
            Trainer.objects.create(user=user, experience="", contact_no="")

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
        fields = ["id", "email", "full_name", "is_trainer", "trainer_profile"]

# --- LOGIN SERIALIZER ---
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("User account is inactive")

        tokens = self.get_tokens_for_user(user)

        return {
            "user": user,
            "tokens": tokens,
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