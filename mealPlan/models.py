from django.db import models
from django.conf import settings

class MealPlan(models.Model):
    mealplan_id = models.AutoField(primary_key=True)
    member_id = models.IntegerField()
    trainer_id = models.IntegerField()

    requestee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requested_mealplans',
        null=True,
        blank=True
    )

    STATUS_CHOICES = [
        ('not_created', 'Not Created'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    PLAN_TYPE_CHOICES = [
        ('personal', 'Personal'),
        ('general', 'General'),
    ]
    plan_type = models.CharField(max_length=10, choices=PLAN_TYPE_CHOICES, default='personal')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_created')
    mealplan_name = models.CharField(max_length=255)
    fitness_goal = models.CharField(max_length=255)
    weight_goal = models.CharField(max_length=255, null=True)
    calorie_intake = models.IntegerField()
    protein = models.IntegerField()
    carbs = models.IntegerField()
    instructions = models.TextField()
    user_allergies = models.TextField(blank=True, null=True, help_text="User-declared allergies")

    def updatePlan(self, meals_data):
        """Updates all meals in the meal plan."""
        self.meals.all().delete()
        for meal_data in meals_data:
            allergens_data = meal_data.pop('allergens', [])
            meal = Meal.objects.create(mealplan=self, **meal_data)
            for allergen in allergens_data:
                Allergen.objects.create(meal=meal, **allergen)
        self.save()

    def adjustMacros(self, new_calories=None, new_protein=None, new_carbs=None):
        """
        Adjusts calories, protein, and carbs if provided.
        """
        if new_calories is not None:
            self.calorie_intake = new_calories
        if new_protein is not None:
            self.protein = new_protein
        if new_carbs is not None:
            self.carbs = new_carbs
        self.save()

class Meal(models.Model):
    mealplan = models.ForeignKey(MealPlan, related_name="meals", on_delete=models.CASCADE)
    meal_name = models.CharField(max_length=255)
    description = models.TextField()
    meal_type = models.CharField(max_length=100)
    calories = models.IntegerField()
    protein = models.IntegerField()
    carbs = models.IntegerField()
    allergens = models.ManyToManyField('Allergen', related_name='meals', blank=True)

class Feedback(models.Model):
    mealplan = models.ForeignKey(MealPlan, related_name="feedbacks", on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Allergen(models.Model):
    allergen_name = models.CharField(max_length=255)
