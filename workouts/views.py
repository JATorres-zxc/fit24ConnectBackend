from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from account.models import CustomUser
from .models import (
    Exercise,
    WorkoutProgram,
    UserSpecificWorkoutProgram,
    WorkoutDay,
    WorkoutExercise
)
from .serializers import (
    ExerciseSerializer,
    WorkoutProgramSerializer,
    UserSpecificWorkoutProgramSerializer,
    WorkoutDaySerializer,
    WorkoutExerciseSerializer
)

class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()

class WorkoutProgramViewSet(viewsets.ModelViewSet):
    queryset = WorkoutProgram.objects.all()
    serializer_class = WorkoutProgramSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = WorkoutProgram.objects.all()
        
        # Filter by program type if provided
        program_type = self.request.query_params.get('type', None)
        if program_type in ['general', 'user_specific']:
            queryset = queryset.filter(program_type=program_type)
        
        # For non-trainers, only show general programs
        if not self.request.user.is_trainer and not self.request.user.is_admin:
            queryset = queryset.filter(program_type='general')
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser | permissions.IsTrainer]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def assign_to_user(self, request, pk=None):
        program = self.get_object()
        if program.program_type != 'general':
            return Response(
                {'error': 'Only general programs can be assigned to users'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserSpecificWorkoutProgramSerializer(
            data={
                'base_program': program.id,
                'assigned_to': request.data.get('user_id'),
                'notes': request.data.get('notes', '')
            },
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserSpecificWorkoutProgramViewSet(viewsets.ModelViewSet):
    serializer_class = UserSpecificWorkoutProgramSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = UserSpecificWorkoutProgram.objects.all()

        if user.is_trainer:
            # Trainers can see programs they've assigned
            queryset = queryset.filter(assigned_by=user)
        elif not user.is_admin:
            # Regular users can only see their own programs
            queryset = queryset.filter(assigned_to=user)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser | permissions.IsTrainer]
        return super().get_permissions()

class WorkoutDayViewSet(viewsets.ModelViewSet):
    queryset = WorkoutDay.objects.all()
    serializer_class = WorkoutDaySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser | permissions.IsTrainer]
        return super().get_permissions()

class WorkoutExerciseViewSet(viewsets.ModelViewSet):
    queryset = WorkoutExercise.objects.all()
    serializer_class = WorkoutExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser | permissions.IsTrainer]
        return super().get_permissions()