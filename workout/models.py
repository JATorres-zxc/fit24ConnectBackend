from django.db import models
from django.conf import settings

class Exercise(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    muscle_group = models.CharField(max_length=255, help_text="Targeted muscle group")
    
    def __str__(self):
        return self.name

class WorkoutProgram(models.Model):
    TRAINING_TYPES = [
        ('free', 'Free Workout'),
        ('trainer_assigned', 'Trainer Assigned'),
    ]

    program_name = models.CharField(max_length=255)
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, blank=True, 
        limit_choices_to={'is_trainer': True}
    )
    fitness_goal = models.CharField(max_length=255)
    duration = models.PositiveIntegerField(help_text="Duration in days")
    intensity_level = models.CharField(max_length=100)
    program_type = models.CharField(max_length=20, choices=TRAINING_TYPES, default='free')

    def __str__(self):
        return self.program_name

class WorkoutExercise(models.Model):
    workout_program = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE, related_name="workout_exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField(default=3)
    reps = models.PositiveIntegerField(default=10)
    rest_time = models.PositiveIntegerField(help_text="Rest time in seconds", default=60)
    duration_per_set = models.PositiveIntegerField(help_text="Duration per set in seconds", default=30)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.exercise.name} - {self.workout_program.program_name}"

class UserWorkout(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workout_program = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE)
    progress = models.JSONField(default=dict, help_text="Tracks workout progress")
    started_on = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.workout_program.program_name}"
