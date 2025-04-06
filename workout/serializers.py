from rest_framework import serializers
from .models import WorkoutProgram, UserWorkout, Exercise, WorkoutExercise

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'

class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise_details = ExerciseSerializer(source="exercise", read_only=True)

    class Meta:
        model = WorkoutExercise
        fields = '__all__'

class WorkoutProgramSerializer(serializers.ModelSerializer):
    trainer_name = serializers.ReadOnlyField(source='trainer.full_name')
    requestee_email = serializers.ReadOnlyField(source='requestee.email')
    workout_exercises = WorkoutExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = WorkoutProgram
        fields = '__all__'

class UserWorkoutSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    workout_program_name = serializers.ReadOnlyField(source='workout_program.program_name')

    class Meta:
        model = UserWorkout
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}  # Ensures 'user' isn't required in request

