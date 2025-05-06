from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'workouts', WorkoutProgramViewSet, basename='workout')

urlpatterns = [
    path('', include(router.urls)),
    path('user-workouts/', UserWorkoutListCreateView.as_view(), name='user-workout-list'),
    path('user-workouts/<int:pk>/', UserWorkoutDetailView.as_view(), name='user-workout-detail'),
    path('exercises/', ExerciseListCreateView.as_view(), name='exercise-list'),
    path('exercises/<int:pk>/', ExerciseDetailView.as_view(), name='exercise-detail'),
    path('workout-exercises/', WorkoutExerciseListCreateView.as_view(), name='workout-exercise-list'),
    path('workout-exercises/<int:pk>/', WorkoutExerciseDetailView.as_view(), name='workout-exercise-detail'),
]
