from rest_framework import generics, permissions
from .models import WorkoutProgram, UserWorkout, Exercise, WorkoutExercise
from .serializers import WorkoutProgramSerializer, UserWorkoutSerializer, ExerciseSerializer, WorkoutExerciseSerializer

class WorkoutProgramListCreateView(generics.ListCreateAPIView):
    queryset = WorkoutProgram.objects.all()
    serializer_class = WorkoutProgramSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated and self.request.user.is_trainer:
            serializer.save(trainer=self.request.user)
        else:
            serializer.save(trainer=None)

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
