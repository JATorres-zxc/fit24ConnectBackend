from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.conf import settings
from .serializers import RegistrationSerializer, LoginSerializer, ForgotPasswordSerializer, TrainerSerializer
from .models import CustomUser, Trainer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import ListAPIView
from .serializers import UserSerializer
from rest_framework.exceptions import PermissionDenied

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
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid or expired refresh token."}, status=status.HTTP_400_BAD_REQUEST)


# Trainer Profile View
class TrainerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve the trainer profile of the logged-in user."""
        if not request.user.is_trainer:
            return Response({"error": "User is not a trainer."}, status=status.HTTP_403_FORBIDDEN)

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
    queryset = CustomUser.objects.filter(is_trainer=False, is_admin=False)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_admin:
            raise PermissionDenied("Only admins can access this data.")
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
