from rest_framework import serializers
from account.models import CustomUser
from .models import (
    Exercise,
    WorkoutProgram,
    UserSpecificWorkoutProgram,
    WorkoutDay,
    WorkoutExercise
)

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(),
        source='exercise',
        write_only=True
    )

    class Meta:
        model = WorkoutExercise
        fields = '__all__'
        extra_kwargs = {
            'workout_day': {'required': False}
        }

class WorkoutDaySerializer(serializers.ModelSerializer):
    exercises = WorkoutExerciseSerializer(many=True, required=False)

    class Meta:
        model = WorkoutDay
        fields = '__all__'
        extra_kwargs = {
            'program': {'required': False}
        }

    def create(self, validated_data):
        exercises_data = validated_data.pop('exercises', [])
        workout_day = WorkoutDay.objects.create(**validated_data)
        
        for exercise_data in exercises_data:
            WorkoutExercise.objects.create(workout_day=workout_day, **exercise_data)
        
        return workout_day

class WorkoutProgramSerializer(serializers.ModelSerializer):
    workout_days = WorkoutDaySerializer(many=True, required=False)
    created_by = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=CustomUser.objects.filter(is_trainer=True)
    )

    class Meta:
        model = WorkoutProgram
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        workout_days_data = validated_data.pop('workout_days', [])
        program = WorkoutProgram.objects.create(**validated_data)
        
        for day_data in workout_days_data:
            exercises_data = day_data.pop('exercises', [])
            workout_day = WorkoutDay.objects.create(program=program, **day_data)
            
            for exercise_data in exercises_data:
                WorkoutExercise.objects.create(workout_day=workout_day, **exercise_data)
        
        return program

class UserSpecificWorkoutProgramSerializer(serializers.ModelSerializer):
    base_program = WorkoutProgramSerializer(read_only=True)
    base_program_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutProgram.objects.filter(program_type='user_specific'),
        source='base_program',
        write_only=True
    )
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(is_trainer=False)
    )
    assigned_by = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=CustomUser.objects.filter(is_trainer=True)
    )

    class Meta:
        model = UserSpecificWorkoutProgram
        fields = '__all__'
        read_only_fields = ('assigned_at', 'modified_at')

    def validate(self, data):
        if data['assigned_by'] == data['assigned_to']:
            raise serializers.ValidationError("Trainer cannot assign program to themselves.")
        return data