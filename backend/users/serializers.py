from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'gender', 'birth_date', 'height_cm', 'weight_kg',
            'activity_level', 'goal', 'bmr', 'tdee', 'daily_calorie_goal',
            'protein_goal_g', 'carbs_goal_g', 'fat_goal_g', 'avatar', 'is_premium'
        ]
        read_only_fields = [
            'bmr', 'tdee', 'daily_calorie_goal',
            'protein_goal_g', 'carbs_goal_g', 'fat_goal_g', 'is_premium'
        ]

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['gender', 'birth_date', 'height_cm', 'weight_kg', 'activity_level', 'goal', 'avatar']
        read_only_fields = ['avatar']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    # This is handled by simplejwt, but we can write a wrapper if we need custom logic
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class NutritionGoalsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'bmr', 'tdee', 'daily_calorie_goal',
            'protein_goal_g', 'carbs_goal_g', 'fat_goal_g'
        ]
