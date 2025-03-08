from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MealPlanViewSet, MealViewSet, FeedbackViewSet, AllergenViewSet

router = DefaultRouter()
router.register(r'mealplans', MealPlanViewSet)
router.register(r'meals', MealViewSet)
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'allergens', AllergenViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
