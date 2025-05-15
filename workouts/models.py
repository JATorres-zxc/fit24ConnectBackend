from django.db import models

class WorkoutProgram(models.Model):
    program_name = models.CharField(max_length=255, blank=True, null=True)
    trainer_id = models.IntegerField()  # Regular integer field for trainer ID
    requestee = models.IntegerField(null=True, blank=True)  # Regular integer field for member ID
    duration = models.PositiveIntegerField(default=30)  # Duration in days
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed')
        ],
        default='pending'
    )
    fitness_goal = models.CharField(max_length=255, default="General Fitness")
    intensity_level = models.CharField(max_length=255, default="Moderate Intensity")

    def __str__(self):
        return f"{self.program_name} (Trainer ID: {self.trainer_id}, Requestee ID: {self.requestee})"


class WorkoutExercise(models.Model):
    program = models.ForeignKey(
        WorkoutProgram,
        on_delete=models.CASCADE,
        related_name='workout_exercises'
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=255, blank=True, null=True)
    muscle_group = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='exercise_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.program.program_name})"


class Feedback(models.Model):
    program = models.ForeignKey(
        WorkoutProgram,
        related_name="feedbacks",
        on_delete=models.CASCADE
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.program.program_name} - {self.created_at}"