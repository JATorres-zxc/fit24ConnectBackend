from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from .models import WorkoutProgram, Feedback
from .serializers import WorkoutProgramSerializer, FeedbackSerializer

class WorkoutProgramViewSet(viewsets.ModelViewSet):
    queryset = WorkoutProgram.objects.all()
    serializer_class = WorkoutProgramSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = WorkoutProgram.objects.all()

        # # Filter programs based on user type
        # if not getattr(self.request.user, 'is_trainer', False):  # Non-staff users
        #     queryset = queryset.filter(requestee=self.request.user.id)

        return queryset


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        program_id = self.request.data.get('program')
        print(f"Received data: {self.request.data}")  # Debugging
        if not program_id:
            raise ValidationError({"error": "program field is required"})
        program = get_object_or_404(WorkoutProgram, pk=program_id)
        serializer.save(program=program)
