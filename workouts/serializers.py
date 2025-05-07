from rest_framework import serializers
from .models import WorkoutProgram, WorkoutExercise, Feedback

from rest_framework import serializers
from .models import WorkoutProgram, WorkoutExercise, Feedback

class WorkoutExerciseSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = WorkoutExercise
        fields = ['id', 'name', 'description', 'muscle_group', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            # If the image is a file, return its full URL
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None  # Return None if no image is provided

    def to_internal_value(self, data):
        # Allow both file uploads and URI links for the image field
        image = data.get('image', None)
        if isinstance(image, str):  # If it's a URI
            data['image'] = image
        return super().to_internal_value(data)


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'program', 'comment', 'created_at']


class WorkoutProgramSerializer(serializers.ModelSerializer):
    workout_exercises = WorkoutExerciseSerializer(many=True, required=False)
    feedbacks = FeedbackSerializer(many=True, read_only=True)
    requestee = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        model = WorkoutProgram
        fields = [
            'id', 'program_name', 'trainer_id', 'requestee', 'status',
            'fitness_goal', 'intensity_level', 'duration', 'workout_exercises', 'feedbacks'
        ]

    def to_internal_value(self, data):
        # Convert requestee to an integer if it's provided as a string
        requestee_value = data.get('requestee')
        if requestee_value is not None:
            try:
                data['requestee'] = int(requestee_value)
            except ValueError:
                raise serializers.ValidationError({"requestee": "Invalid integer value."})

        return super().to_internal_value(data)

    def create(self, validated_data):
        exercises_data = validated_data.pop('workout_exercises', [])
        program = WorkoutProgram.objects.create(**validated_data)

        for exercise_data in exercises_data:
            WorkoutExercise.objects.create(program=program, **exercise_data)

        return program

    def update(self, instance, validated_data):
        exercises_data = validated_data.pop('workout_exercises', [])
        instance = super().update(instance, validated_data)

        # Clear existing exercises and recreate them
        instance.workout_exercises.all().delete()
        for exercise_data in exercises_data:
            WorkoutExercise.objects.create(program=instance, **exercise_data)

        return instance