from django.db import models

class MealPlan(models.Model):
    mealplan_id = models.AutoField(primary_key=True)
    member_id = models.IntegerField()
    trainer_id = models.IntegerField()
    mealplan_name = models.CharField(max_length=255)
    fitness_goal = models.CharField(max_length=255)
    calorie_intake = models.IntegerField()
    protein = models.IntegerField()
    carbs = models.IntegerField()
    instructions = models.TextField()

    def updatePlan(self, meals_data):
        """
        Updates all meals in the meal plan.
        Expects `meals_data` to be a list of dictionaries containing meal details.
        """
        self.meals.all().delete()
        for meal_data in meals_data:
            Meal.objects.create(mealplan=self, **meal_data)
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

class Feedback(models.Model):
    mealplan = models.ForeignKey(MealPlan, related_name="feedbacks", on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Allergen(models.Model):
    mealplan = models.ForeignKey(MealPlan, related_name="allergens", on_delete=models.CASCADE)
    allergen_name = models.CharField(max_length=255)
