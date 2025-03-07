from rest_framework import serializers
from .models import MealPlan, Meal, Feedback, Allergen

class MealSerializer(serializers.ModelSerializer):
    mealplan = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Meal
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class AllergenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergen
        fields = '__all__'

class MealPlanSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True)  # Allow nested creation

    class Meta:
        model = MealPlan
        fields = '__all__'

    def create(self, validated_data):
        """
        Custom create method to handle nested meals.
        """
        meals_data = validated_data.pop('meals', [])  # Extract meals from request
        meal_plan = MealPlan.objects.create(**validated_data)  # Create MealPlan first

        # Create meals linked to the meal plan
        for meal_data in meals_data:
            Meal.objects.create(mealplan=meal_plan, **meal_data)

        return meal_plan

    def update(self, instance, validated_data):
        """
        Custom update method to handle nested meals.
        """
        meals_data = validated_data.pop('meals', [])  # Extract meals data from request

        # Update MealPlan fields
        instance.mealplan_name = validated_data.get('mealplan_name', instance.mealplan_name)
        instance.fitness_goal = validated_data.get('fitness_goal', instance.fitness_goal)
        instance.calorie_intake = validated_data.get('calorie_intake', instance.calorie_intake)
        instance.protein = validated_data.get('protein', instance.protein)
        instance.carbs = validated_data.get('carbs', instance.carbs)
        instance.instructions = validated_data.get('instructions', instance.instructions)
        instance.save()

        # Delete existing meals and create new ones
        instance.meals.all().delete()
        for meal_data in meals_data:
            Meal.objects.create(mealplan=instance, **meal_data)

        return instance
