from django.db import models
from account.models import CustomUser

class Exercise(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    muscle_group = models.CharField(max_length=255)
    equipment_needed = models.CharField(max_length=255)
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced')
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class WorkoutProgram(models.Model):
    PROGRAM_TYPES = [
        ('general', 'General'),
        ('user_specific', 'User Specific')
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES, default='general')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_workout_programs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration_weeks = models.PositiveIntegerField(default=4)
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced')
        ],
        default='beginner'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_program_type_display()})"

class UserSpecificWorkoutProgram(models.Model):
    base_program = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE, related_name='user_specific_versions')
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_workout_programs')
    assigned_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_workouts')
    assigned_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('base_program', 'assigned_to')
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.base_program.name} - {self.assigned_to.email}"

class WorkoutDay(models.Model):
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    program = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE, related_name='workout_days')
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['program', 'day']
        unique_together = ('program', 'day')

    def __str__(self):
        return f"{self.program.name} - {self.get_day_display()}"

class WorkoutExercise(models.Model):
    workout_day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField()
    reps = models.CharField(max_length=50)  # Can be "8-12" or "AMRAP" etc.
    rest_interval = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.exercise.name} for {self.workout_day}"