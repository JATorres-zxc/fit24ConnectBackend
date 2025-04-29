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
from rest_framework.permissions import IsAuthenticated

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

        # Get the user's declared allergens
        user_allergens = Allergen.objects.filter(name__in=request.user.user_allergies.split(','))

        # Filter meals based on allergens
        incompatible_meals = []
        for meal_data in meals_data:
            meal_id = meal_data.get('meal_id')
            meal = get_object_or_404(Meal, id=meal_id)

            # Check if any allergens in the meal are in the user's declared allergens
            meal_allergens = meal.allergens.all()
            if meal_allergens.filter(id__in=user_allergens.values_list('id', flat=True)).exists():
                incompatible_meals.append(meal.id)

        if incompatible_meals:
            return Response(
                {'error': f'Meals with the following IDs contain allergens: {incompatible_meals}'}, status=400
            )

        mealplan.updatePlan(meals_data)
        return Response({'status': 'meal plan updated'})

    def perform_create(self, serializer):
        """
        Create a new meal plan. Set requestee to the current user.
        Only trainers users can create general meal plans.
        """
        plan_type = self.request.data.get('plan_type', 'personal')

        if plan_type == 'general':
            if not self.request.user.is_trainer:
                raise PermissionDenied("Only trainer can create general meal plans.")
        elif plan_type == 'personal':
            raise PermissionDenied("Use the request_plan endpoint to request a personal meal plan.")

        serializer.save(requestee=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def request_plan(self, request):
        """
        Allows a member to request a personal meal plan.
        Requires a trainer_id to be specified.
        """
        if getattr(request.user, 'is_trainer', False):
            return Response({'error': 'Trainers cannot request meal plans.'}, status=403)

        trainer_id = request.data.get('trainer_id')
        if not trainer_id:
            raise ValidationError({'trainer_id': 'This field is required.'})

        # Optional: validate if trainer_id exists and is actually a trainer
        from account.models import CustomUser
        try:
            trainer = CustomUser.objects.get(id=trainer_id, is_trainer=True)
        except CustomUser.DoesNotExist:
            raise ValidationError({'trainer_id': 'Invalid trainer ID or user is not a trainer.'})

        # Check if the user already has a pending personal meal plan
        existing = MealPlan.objects.filter(
            requestee=request.user,
            plan_type='personal',
            status__in=['in_progress', 'not_created']
        ).exists()

        if existing:
            return Response({'error': 'You already have a pending personal meal plan.'}, status=400)

        # Create the meal plan and filter based on allergens
        meal_plan = MealPlan.objects.create(
            requestee=request.user,
            member_id=request.user.id,
            trainer_id=trainer_id,
            plan_type='personal',
            status='in_progress',
            mealplan_name='',
            fitness_goal='',
            weight_goal='',
            calorie_intake=0,
            protein=0,
            carbs=0,
            instructions=''
        )

        serializer = MealPlanSerializer(meal_plan)
        return Response(serializer.data, status=201)

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
