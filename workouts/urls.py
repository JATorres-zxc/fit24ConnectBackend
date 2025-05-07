from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExerciseViewSet,
    WorkoutProgramViewSet,
    UserSpecificWorkoutProgramViewSet,
    WorkoutDayViewSet,
    WorkoutExerciseViewSet
)

router = DefaultRouter()
router.register(r'exercises', ExerciseViewSet, basename='exercise')
router.register(r'workout-programs', WorkoutProgramViewSet, basename='workoutprogram')
router.register(r'user-specific-programs', UserSpecificWorkoutProgramViewSet, basename='userspecificprogram')
router.register(r'workout-days', WorkoutDayViewSet, basename='workoutday')
router.register(r'workout-exercises', WorkoutExerciseViewSet, basename='workoutexercise')

urlpatterns = [
    path('', include(router.urls)),
]