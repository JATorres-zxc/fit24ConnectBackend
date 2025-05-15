from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkoutProgramViewSet, FeedbackViewSet

router = DefaultRouter()
router.register(r'workout-programs', WorkoutProgramViewSet, basename='workoutprogram')
router.register(r'feedback', FeedbackViewSet, basename='feedback')

urlpatterns = [
    path('', include(router.urls)),
]