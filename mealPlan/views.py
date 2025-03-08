from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import MealPlan, Meal, Feedback, Allergen
from .serializers import MealPlanSerializer, MealSerializer, FeedbackSerializer, AllergenSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404

class MealPlanViewSet(viewsets.ModelViewSet):
    queryset = MealPlan.objects.all()
    serializer_class = MealPlanSerializer

    @action(detail=True, methods=['patch'])
    def adjust_macros(self, request, pk=None):
        """
        Adjusts calories, protein, and carbs in the meal plan.
        """
        mealplan = self.get_object()
        new_calories = request.data.get('newCalories')
        new_protein = request.data.get('newProtein')
        new_carbs = request.data.get('newCarbs')

        mealplan.adjustMacros(new_calories, new_protein, new_carbs)
        return Response({'status': 'macros updated'})

    @action(detail=True, methods=['put'])
    def update_meal_plan(self, request, pk=None):
        """
        Updates the entire meal plan including all meals.
        """
        mealplan = self.get_object()
        meals_data = request.data.get('meals', [])

        if meals_data:
            mealplan.updatePlan(meals_data)
            return Response({'status': 'meal plan updated'})

        return Response({'error': 'Invalid input'}, status=400)

class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer

    def perform_create(self, serializer):
        mealplan_id = self.request.data.get('mealplan')
        
        if not mealplan_id:  
            return Response({"error": "mealplan_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if mealplan exists
        mealplan = get_object_or_404(MealPlan, pk=mealplan_id)
        
        serializer.save(mealplan=mealplan)


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

class AllergenViewSet(viewsets.ModelViewSet):
    queryset = Allergen.objects.all()
    serializer_class = AllergenSerializer
