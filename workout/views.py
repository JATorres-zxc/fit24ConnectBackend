from rest_framework import generics, permissions
from .models import WorkoutProgram, UserWorkout, Exercise, WorkoutExercise
from .serializers import WorkoutProgramSerializer, UserWorkoutSerializer, ExerciseSerializer, WorkoutExerciseSerializer

class WorkoutProgramListCreateView(generics.ListCreateAPIView):
    queryset = WorkoutProgram.objects.all()
    serializer_class = WorkoutProgramSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        trainer = self.request.user if self.request.user.is_authenticated and self.request.user.is_trainer else None
        requestee_id = self.request.data.get("requestee")  # expects `requestee` in payload

        requestee = None
        if requestee_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                requestee = User.objects.get(id=requestee_id)
            except User.DoesNotExist:
                pass

        serializer.save(trainer=trainer, requestee=requestee)

    # trainers to list workouts they've made for a specific user
    def get_queryset(self):
        queryset = WorkoutProgram.objects.all()
        requestee_id = self.request.query_params.get('requestee')
        status = self.request.query_params.get('status')

        if requestee_id:
            queryset = queryset.filter(requestee_id=requestee_id)
        if status:
            queryset = queryset.filter(status=status)

        return queryset

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
