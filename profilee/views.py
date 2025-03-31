from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from account.models import CustomUser
from .serializers import ProfileSerializer

class ProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class ProfileDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = ProfileSerializer(user)
        return Response(serializer.data)
