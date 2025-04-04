from rest_framework import serializers
from .models import MealPlan, Meal, Feedback, Allergen
from account.models import CustomUser

class AllergenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergen
        fields = '__all__'

class MealSerializer(serializers.ModelSerializer):
    allergens = AllergenSerializer(many=True, required=False)  # Include allergens in meals

    class Meta:
        model = Meal
        fields = '__all__'

    def create(self, validated_data):
        allergens_data = validated_data.pop('allergens', [])
        meal = Meal.objects.create(**validated_data)

        for allergen in allergens_data:
            Allergen.objects.create(meal=meal, **allergen)

        return meal

    def update(self, instance, validated_data):
        allergens_data = validated_data.pop('allergens', [])

        instance.meal_name = validated_data.get('meal_name', instance.meal_name)
        instance.description = validated_data.get('description', instance.description)
        instance.meal_type = validated_data.get('meal_type', instance.meal_type)
        instance.calories = validated_data.get('calories', instance.calories)
        instance.protein = validated_data.get('protein', instance.protein)
        instance.carbs = validated_data.get('carbs', instance.carbs)
        instance.save()

        instance.allergens.all().delete()
        for allergen in allergens_data:
            Allergen.objects.create(meal=instance, **allergen)

        return instance

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class MealPlanSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True, required=False)
    requestee_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='requestee',
        required=False
    )
    feedbacks = FeedbackSerializer(many=True, read_only=True) 
    
    class Meta:
        model = MealPlan
        fields = '__all__'

    def create(self, validated_data):
        meals_data = validated_data.pop('meals', [])
        meal_plan = MealPlan.objects.create(**validated_data)

        for meal_data in meals_data:
            allergens_data = meal_data.pop('allergens', [])
            meal = Meal.objects.create(mealplan=meal_plan, **meal_data)

            for allergen in allergens_data:
                Allergen.objects.create(meal=meal, **allergen)

        return meal_plan

    def update(self, instance, validated_data):
        meals_data = validated_data.pop('meals', [])

        instance.mealplan_name = validated_data.get('mealplan_name', instance.mealplan_name)
        instance.fitness_goal = validated_data.get('fitness_goal', instance.fitness_goal)
        instance.weight_goal = validated_data.get('weight_goal', instance.weight_goal)
        instance.calorie_intake = validated_data.get('calorie_intake', instance.calorie_intake)
        instance.protein = validated_data.get('protein', instance.protein)
        instance.carbs = validated_data.get('carbs', instance.carbs)
        instance.instructions = validated_data.get('instructions', instance.instructions)
        instance.save()

        instance.meals.all().delete()
        for meal_data in meals_data:
            allergens_data = meal_data.pop('allergens', [])
            meal = Meal.objects.create(mealplan=instance, **meal_data)

            for allergen in allergens_data:
                Allergen.objects.create(meal=meal, **allergen)

        return instance

