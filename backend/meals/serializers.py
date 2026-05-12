from rest_framework import serializers
from .models import Meal, MealImageAnalysis, MealItem, WaterLog, WeightLog
from food.serializers import FoodItemSerializer

class MealItemSerializer(serializers.ModelSerializer):
    food_item_detail = FoodItemSerializer(source='food_item', read_only=True)
    
    class Meta:
        model = MealItem
        fields = ['id', 'meal', 'food_item', 'food_item_detail', 'weight_g', 'calories', 'protein', 'carbs', 'fat', 'created_at']
        read_only_fields = ['meal', 'calories', 'protein', 'carbs', 'fat']

class MealSerializer(serializers.ModelSerializer):
    items = MealItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Meal
        fields = ['id', 'user', 'date', 'meal_type', 'total_calories', 'total_protein', 'total_carbs', 'total_fat', 'items', 'created_at']
        read_only_fields = ['user', 'total_calories', 'total_protein', 'total_carbs', 'total_fat']

class MealItemCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealItem
        fields = ['id', 'food_item', 'weight_g', 'calories', 'protein', 'carbs', 'fat']
        read_only_fields = ['id', 'calories', 'protein', 'carbs', 'fat']

    def validate_weight_g(self, value):
        if value <= 0:
            raise serializers.ValidationError("Gramm miqdori 0 dan katta bo'lishi kerak.")
        return value

class MealImageAnalyzeInputSerializer(serializers.Serializer):
    image = serializers.ImageField()
    date = serializers.DateField()
    meal_type = serializers.ChoiceField(choices=Meal.MEAL_TYPES)

class MealImageAnalysisSerializer(serializers.ModelSerializer):
    meal_item_detail = MealItemSerializer(source='meal_item', read_only=True)

    class Meta:
        model = MealImageAnalysis
        fields = [
            'id', 'meal', 'meal_item', 'meal_item_detail', 'date', 'meal_type', 'image', 'status',
            'detected_food_name', 'estimated_weight_g', 'estimated_calories',
            'estimated_protein', 'estimated_carbs', 'estimated_fat', 'confidence',
            'notes', 'error_message', 'created_at'
        ]
        read_only_fields = fields

class WaterLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterLog
        fields = '__all__'
        read_only_fields = ['user']

    def validate_amount_ml(self, value):
        if value <= 0:
            raise serializers.ValidationError("Suv miqdori 0 dan katta bo'lishi kerak.")
        return value

class WeightLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightLog
        fields = '__all__'
        read_only_fields = ['user']

    def validate_weight_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("Vazn 0 dan katta bo'lishi kerak.")
        return value
