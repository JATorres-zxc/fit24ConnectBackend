from django.urls import path
from .views import (
    WorkoutProgramListCreateView, WorkoutProgramDetailView, 
    UserWorkoutListCreateView, UserWorkoutDetailView,
    ExerciseListCreateView, ExerciseDetailView,
    WorkoutExerciseListCreateView, WorkoutExerciseDetailView
)

urlpatterns = [
    path('workouts/', WorkoutProgramListCreateView.as_view(), name='workout-list'),
    path('workouts/<int:pk>/', WorkoutProgramDetailView.as_view(), name='workout-detail'),
    path('user-workouts/', UserWorkoutListCreateView.as_view(), name='user-workout-list'),
    path('user-workouts/<int:pk>/', UserWorkoutDetailView.as_view(), name='user-workout-detail'),
    path('exercises/', ExerciseListCreateView.as_view(), name='exercise-list'),
    path('exercises/<int:pk>/', ExerciseDetailView.as_view(), name='exercise-detail'),
    path('workout-exercises/', WorkoutExerciseListCreateView.as_view(), name='workout-exercise-list'),
    path('workout-exercises/<int:pk>/', WorkoutExerciseDetailView.as_view(), name='workout-exercise-detail'),
]
