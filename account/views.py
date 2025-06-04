from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.conf import settings
from .serializers import *
from .models import CustomUser, Trainer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import permissions
from rest_framework import generics
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import ListAPIView
from .serializers import UserSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"success": True, "message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = data["user"]
            tokens = data["tokens"]

            user_data = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                # "is_trainer": user.is_trainer,
                "role":user.role
            }

            # Include trainer details if the user is a trainer
            if user.is_trainer:
                try:
                    trainer_profile = Trainer.objects.get(user=user)
                    user_data["trainer_profile"] = TrainerSerializer(trainer_profile).data
                except Trainer.DoesNotExist:
                    user_data["trainer_profile"] = None

            return Response({
                "success": True,
                "message": "Login successful",
                "user": user_data,
                "tokens": tokens
            }, status=status.HTTP_200_OK)
        
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
            
            send_mail(
                "Password Reset",
                "Click the link to reset your password.",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can logout

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Clear any stored tokens on the frontend by returning instructions
            return Response({
                "message": "Logged out successfully.",
                "clear_tokens": True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Trainer Profile View
class TrainerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve the trainer profile of the logged-in user."""
        if not request.user.is_trainer:
            return Response({"error": "User is not a trainer."}, status=status.HTTP_403_FORBIDDEN)

        # Ensure Trainer profile exists if user is a trainer
        request.user.ensure_trainer_profile
        try:
            trainer = Trainer.objects.get(user=request.user)
            serializer = TrainerSerializer(trainer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Trainer.DoesNotExist:
            return Response({"error": "Trainer profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        """Update trainer profile details."""
        if not request.user.is_trainer:
            return Response({"error": "User is not a trainer."}, status=status.HTTP_403_FORBIDDEN)

        # Ensure Trainer profile exists if user is a trainer
        request.user.ensure_trainer_profile
        try:
            trainer = Trainer.objects.get(user=request.user)
            serializer = TrainerSerializer(trainer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Trainer.DoesNotExist:
            return Response({"error": "Trainer profile not found."}, status=status.HTTP_404_NOT_FOUND)

class TrainerListView(ListAPIView):
    queryset = Trainer.objects.select_related('user').filter(user__is_trainer=True)
    serializer_class = TrainerSerializer
    permission_classes = [IsAuthenticated]

# GET /trainers/
# [
#   {
#     "id": 1,
#     "user": {
#       "id": 2,
#       "email": "trainer1@example.com",
#       "full_name": "Trainer One"
#     },
#     "experience": "5 years of strength training",
#     "contact_no": "1234567890"
#   },
#   {
#     "id": 2,
#     "user": {
#       "id": 4,
#       "email": "trainer2@example.com",
#       "full_name": "Trainer Two"
#     },
#     "experience": "Certified nutritionist",
#     "contact_no": "0987654321"
#   }
# ]


class MemberListView(ListAPIView):
    queryset = CustomUser.objects.filter(
        is_trainer=False,
        is_admin=False,
        is_superuser=False,
        is_staff=False
    )
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not (user.is_admin or user.is_trainer):
            raise PermissionDenied("Only admins and trainer can access this data.")
        return super().get_queryset()

# GET /members/
# [
#   {
#     "id": 5,
#     "email": "jane@example.com",
#     "full_name": "Jane Doe",
#     "is_trainer": false,
#     "trainer_profile": null
#   },
#   {
#     "id": 7,
#     "email": "mark@example.com",
#     "full_name": "Mark Smith",
#     "is_trainer": false,
#     "trainer_profile": null
#   }
# ]

class TrainerStatusUpdateView(APIView):
    def post(self, request, user_id, action):
        admin_user = request.user

        if not admin_user.is_admin:
            return Response({"detail": "You do not have permission to perform this action."}, status=403)

        try:
            target_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

        # ✅ Fix inconsistencies before proceeding
        self.fix_trainer_inconsistency(target_user)

        is_in_trainer_table = Trainer.objects.filter(user=target_user).exists()

        if action == 'make':
            if target_user.is_trainer and is_in_trainer_table:
                return Response({"detail": "User is already a trainer."}, status=400)

            target_user.is_trainer = True
            target_user.save()

            if not is_in_trainer_table:
                Trainer.objects.get_or_create(user=target_user)

            return Response({"detail": "User is now a trainer."})

        elif action == 'remove':
            if not target_user.is_trainer and not is_in_trainer_table:
                return Response({"detail": "User is not a trainer."}, status=400)

            target_user.is_trainer = False
            target_user.save()

            if is_in_trainer_table:
                Trainer.objects.filter(user=target_user).delete()

            return Response({"detail": "Trainer status removed."})

        else:
            return Response({"detail": "Invalid action."}, status=400)

    def fix_trainer_inconsistency(self, user):
        """
        Automatically aligns is_trainer flag with Trainer table.
        """
        trainer_exists = Trainer.objects.filter(user=user).exists()
        if trainer_exists and not user.is_trainer:
            user.is_trainer = True
            user.save()
        elif not trainer_exists and user.is_trainer:
            user.is_trainer = False
            user.save()
# POST /api/account/trainer-status/5/assign/
# Authorization: Bearer <admin_token>

class AdminUpdateMembershipTypeView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = MembershipTypeUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['patch']  # Only allow PATCH requests
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Just update the membership type
        instance.type_of_membership = serializer.validated_data['type_of_membership']
        instance.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class MembershipStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, user_id):
        try:
            member = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        serializer = MembershipStatusUpdateSerializer(member, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Membership dates updated successfully.",
                "is_active": member.is_active,
                "data": serializer.data
            })
        return Response(serializer.errors, status=400)
# PATCH Payload example:
# {
#   "membership_start_date": "2025-05-01",
#   "membership_end_date": "2025-08-01"
# }