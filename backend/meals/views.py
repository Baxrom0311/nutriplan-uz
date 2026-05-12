from decimal import Decimal

from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from datetime import datetime

from food.models import FoodCategory, FoodItem
from .ai_analysis import (
    FoodVisionAnalysisError,
    FoodVisionResult,
    FoodVisionServiceNotConfigured,
    analyze_meal_photo,
)
from .models import Meal, MealImageAnalysis, MealItem, WaterLog, WeightLog
from .serializers import (
    MealSerializer, 
    MealItemCreateUpdateSerializer,
    MealImageAnalyzeInputSerializer,
    MealImageAnalysisSerializer,
    WaterLogSerializer,
    WeightLogSerializer
)


def _build_photo_analysis_context(user, date_obj):
    profile = getattr(user, 'profile', None)
    meals = Meal.objects.filter(user=user, date=date_obj).prefetch_related('items__food_item')
    consumed_cals = sum(meal.total_calories for meal in meals)
    consumed_protein = sum(meal.total_protein for meal in meals)
    consumed_carbs = sum(meal.total_carbs for meal in meals)
    consumed_fat = sum(meal.total_fat for meal in meals)

    return (
        f"Jins: {profile.get_gender_display() if profile and profile.gender else 'noaniq'}; "
        f"bo'y: {profile.height_cm if profile else 'noaniq'} cm; "
        f"vazn: {profile.weight_kg if profile else 'noaniq'} kg; "
        f"maqsad: {profile.get_goal_display() if profile and profile.goal else 'noaniq'}; "
        f"kunlik kaloriya maqsadi: {profile.daily_calorie_goal if profile and profile.daily_calorie_goal else 2000} kkal; "
        f"shu kungacha iste'mol: {consumed_cals} kkal, protein {consumed_protein} g, "
        f"uglevod {consumed_carbs} g, yog' {consumed_fat} g."
    )


def _per_100g(total, weight_g):
    if weight_g <= 0:
        return Decimal('0')
    return (total * Decimal('100')) / weight_g


def _create_meal_item_from_analysis(user, meal, analysis, result: FoodVisionResult):
    category, _ = FoodCategory.objects.get_or_create(
        name='AI Photo Analysis',
        defaults={'name_uz': 'AI rasm tahlili'}
    )
    food_item = FoodItem.objects.create(
        category=category,
        name=result.food_name,
        name_uz=result.food_name,
        calories_per_100g=_per_100g(result.calories, result.estimated_weight_g),
        protein_per_100g=_per_100g(result.protein, result.estimated_weight_g),
        carbs_per_100g=_per_100g(result.carbs, result.estimated_weight_g),
        fat_per_100g=_per_100g(result.fat, result.estimated_weight_g),
        source='manual',
        external_id=f'photo-analysis:{analysis.id}',
        image_url='',
        is_verified=False,
        created_by=user,
    )
    return MealItem.objects.create(
        meal=meal,
        food_item=food_item,
        weight_g=result.estimated_weight_g,
    )

class MealListCreateView(generics.ListCreateAPIView):
    serializer_class = MealSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Meal.objects.none()
        queryset = Meal.objects.filter(user=self.request.user)
        date_str = self.request.query_params.get('date')
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(date=date_obj)
            except ValueError:
                pass
        return queryset.order_by('-date', '-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MealDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MealSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Meal.objects.none()
        return Meal.objects.filter(user=self.request.user)

class MealItemCreateView(generics.CreateAPIView):
    serializer_class = MealItemCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        meal_id = self.kwargs.get('meal_pk')
        meal = get_object_or_404(Meal, pk=meal_id, user=self.request.user)
        serializer.save(meal=meal)

class MealItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MealItemCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MealItem.objects.none()
        return MealItem.objects.filter(meal__user=self.request.user)

class MealImageAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        input_serializer = MealImageAnalyzeInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        date_obj = input_serializer.validated_data['date']
        meal_type = input_serializer.validated_data['meal_type']
        image = input_serializer.validated_data['image']

        analysis = MealImageAnalysis.objects.create(
            user=request.user,
            date=date_obj,
            meal_type=meal_type,
            image=image,
        )

        try:
            result = analyze_meal_photo(
                analysis.image,
                user_context=_build_photo_analysis_context(request.user, date_obj),
            )
        except FoodVisionServiceNotConfigured as exc:
            analysis.status = 'failed'
            analysis.error_message = str(exc)
            analysis.save(update_fields=['status', 'error_message', 'updated_at'])
            return Response(
                {'detail': str(exc), 'analysis': MealImageAnalysisSerializer(analysis).data},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except FoodVisionAnalysisError as exc:
            analysis.status = 'failed'
            analysis.error_message = str(exc)
            analysis.save(update_fields=['status', 'error_message', 'updated_at'])
            return Response(
                {'detail': str(exc), 'analysis': MealImageAnalysisSerializer(analysis).data},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        meal, _ = Meal.objects.get_or_create(
            user=request.user,
            date=date_obj,
            meal_type=meal_type,
        )
        meal_item = _create_meal_item_from_analysis(request.user, meal, analysis, result)

        analysis.meal = meal
        analysis.meal_item = meal_item
        analysis.status = 'processed'
        analysis.detected_food_name = result.food_name
        analysis.estimated_weight_g = result.estimated_weight_g
        analysis.estimated_calories = result.calories
        analysis.estimated_protein = result.protein
        analysis.estimated_carbs = result.carbs
        analysis.estimated_fat = result.fat
        analysis.confidence = result.confidence
        analysis.notes = result.notes_uz
        analysis.raw_response = result.raw
        analysis.save()

        return Response(MealImageAnalysisSerializer(analysis).data, status=status.HTTP_201_CREATED)

class WaterLogListCreateView(generics.ListCreateAPIView):
    serializer_class = WaterLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WaterLog.objects.none()
        queryset = WaterLog.objects.filter(user=self.request.user)
        date_str = self.request.query_params.get('date')
        if date_str:
            queryset = queryset.filter(date=date_str)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WaterLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WaterLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WaterLog.objects.none()
        return WaterLog.objects.filter(user=self.request.user)

class WeightLogListCreateView(generics.ListCreateAPIView):
    serializer_class = WeightLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WeightLog.objects.none()
        return WeightLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WeightLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WeightLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WeightLog.objects.none()
        return WeightLog.objects.filter(user=self.request.user)
