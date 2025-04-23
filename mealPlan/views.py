from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import MealPlan, Meal, Feedback, Allergen
from .serializers import MealPlanSerializer, MealSerializer, FeedbackSerializer, AllergenSerializer
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from account.serializers import UserSerializer
from rest_framework.exceptions import PermissionDenied

class MealPlanViewSet(viewsets.ModelViewSet):
    queryset = MealPlan.objects.all()
    serializer_class = MealPlanSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        requested_status = data.get('status')

        # Prevent members from setting status to completed
        if requested_status == 'completed' and not getattr(request.user, 'is_trainer', False):
            return Response({'error': 'Only trainers can publish (complete) the meal plan.'}, status=403)

        # Enforce who can update the status
        if instance.plan_type == 'personal' and requested_status:
            if instance.status == 'not_created' and requested_status == 'in_progress':
                if request.user != instance.requestee:
                    return Response({'error': 'Only the requestee can mark the plan as in progress.'}, status=403)
            elif instance.status == 'in_progress' and requested_status == 'completed':
                if not getattr(request.user, 'is_trainer', False):
                    return Response({'error': 'Only trainers can mark the plan as completed.'}, status=403)
            elif requested_status != instance.status:
                return Response({'error': 'Invalid status transition.'}, status=400)

        # If user is not a trainer and is not just changing the status to 'in_progress', block changes
        if instance.plan_type == 'personal' and not getattr(request.user, 'is_trainer', False):
            # Allow only changing the status to 'in_progress'
            allowed_fields = {'status'}
            if not set(data.keys()).issubset(allowed_fields):
                return Response({'error': 'You can only mark the meal plan as in progress. Other edits require a trainer.'}, status=403)

        return super().update(request, *args, **kwargs)

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
        Automatically sets status to 'completed' if user is a trainer.
        """
        mealplan = self.get_object()
        meals_data = request.data.get('meals', [])

        if not meals_data:
            return Response({'error': 'Invalid input'}, status=400)

        # Only trainers can complete meal plans
        if mealplan.plan_type == 'personal':
            if not getattr(request.user, 'is_trainer', False):
                return Response({'error': 'Only trainers can publish the meal plan.'}, status=403)
            mealplan.status = 'completed'
            mealplan.save()

        mealplan.updatePlan(meals_data)
        return Response({'status': 'meal plan updated'})

    def perform_create(self, serializer):
        """
        Create a new meal plan. Set requestee to the current user.
        Only staff users can create general meal plans.
        """
        plan_type = self.request.data.get('plan_type', 'personal')
        if plan_type == 'general' and not self.request.user.is_staff:
            raise PermissionDenied("Only admins can create general meal plans.")

        serializer.save(requestee=self.request.user)
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

    def perform_create(self, serializer):
        mealplan_id = self.request.data.get('mealplan')

        if not mealplan_id:
            raise ValidationError({"error": "mealplan_id is required"})

        # Check if mealplan exists
        mealplan = get_object_or_404(MealPlan, pk=mealplan_id)

        # Automatically associate the feedback with the mealplan
        serializer.save(mealplan=mealplan)

class AllergenViewSet(viewsets.ModelViewSet):
    queryset = Allergen.objects.all()
    serializer_class = AllergenSerializer
