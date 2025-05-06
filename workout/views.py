from rest_framework import generics, permissions
from .models import WorkoutProgram, UserWorkout, Exercise, WorkoutExercise
from .serializers import WorkoutProgramSerializer, UserWorkoutSerializer, ExerciseSerializer, WorkoutExerciseSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response

class WorkoutProgramViewSet(viewsets.ModelViewSet):
    queryset = WorkoutProgram.objects.all()
    serializer_class = WorkoutProgramSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = WorkoutProgram.objects.all()
        requestee_id = self.request.query_params.get('requestee')
        status = self.request.query_params.get('status')
        if requestee_id:
            queryset = queryset.filter(requestee_id=requestee_id)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        trainer = self.request.user if self.request.user.is_authenticated and self.request.user.is_trainer else None
        requestee_id = self.request.data.get("requestee")
        requestee = None
        if requestee_id:
            try:
                User = get_user_model()
                requestee = User.objects.get(id=requestee_id)
            except User.DoesNotExist:
                pass
        serializer.save(trainer=trainer, requestee=requestee)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def request_workout(self, request):
        """
        Allows a member to request a personal workout plan.
        Creates an empty WorkoutProgram with status 'in_progress'.
        """
        if getattr(request.user, 'is_trainer', True):
            return Response({'error': 'Trainers cannot request workouts.'}, status=403)

        workout = WorkoutProgram.objects.create(
            requestee=request.user,
            trainer=None,
            program_name='',
            fitness_goal='',
            duration=0,
            intensity_level='',
            status='in_progress',
        )
        serializer = self.get_serializer(workout)
        return Response(serializer.data, status=201)

class WorkoutProgramDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WorkoutProgram.objects.all()
    serializer_class = WorkoutProgramSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserWorkoutListCreateView(generics.ListCreateAPIView):
    serializer_class = UserWorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserWorkout.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        print(f"User in perform_create: {self.request.user}")  # Debugging
        serializer.save(user=self.request.user)

class UserWorkoutDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserWorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserWorkout.objects.filter(user=self.request.user)

class ExerciseListCreateView(generics.ListCreateAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.AllowAny]

class ExerciseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

class WorkoutExerciseListCreateView(generics.ListCreateAPIView):
    queryset = WorkoutExercise.objects.all()
    serializer_class = WorkoutExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

class WorkoutExerciseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WorkoutExercise.objects.all()
    serializer_class = WorkoutExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]
