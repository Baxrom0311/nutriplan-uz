from rest_framework import serializers
from .models import FoodCategory, FoodItem

class FoodCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodCategory
        fields = '__all__'

class FoodItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_name_uz = serializers.CharField(source='category.name_uz', read_only=True)
    
    class Meta:
        model = FoodItem
        fields = '__all__'

class FoodItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = [
            'category', 'name', 'name_uz', 'barcode', 'brand',
            'calories_per_100g', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g',
            'fiber_per_100g', 'sugar_per_100g', 'sodium_per_100g',
            'image_url'
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        if user.is_authenticated:
            validated_data['created_by'] = user
        return super().create(validated_data)

class FoodItemSearchSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_name_uz = serializers.CharField(source='category.name_uz', read_only=True)

    class Meta:
        model = FoodItem
        fields = [
            'id', 'name', 'name_uz', 'barcode', 'brand',
            'calories_per_100g', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g',
            'fiber_per_100g', 'sugar_per_100g', 'sodium_per_100g',
            'source', 'image_url', 'is_verified',
            'category_name', 'category_name_uz'
        ]
