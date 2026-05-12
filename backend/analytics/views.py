from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from meals.models import Meal, WaterLog, WeightLog
from meals.serializers import MealSerializer

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = getattr(user, 'profile', None)
        
        date_str = request.query_params.get('date')
        if not date_str:
            target_date = timezone.now().date()
        else:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                target_date = timezone.now().date()

        # Bugungi ovqatlar
        meals = Meal.objects.filter(user=user, date=target_date).prefetch_related('items__food_item')
        consumed_cals = float(sum(meal.total_calories for meal in meals))
        consumed_protein = float(sum(meal.total_protein for meal in meals))
        consumed_carbs = float(sum(meal.total_carbs for meal in meals))
        consumed_fat = float(sum(meal.total_fat for meal in meals))
        
        # Bugungi suv
        water_logs = WaterLog.objects.filter(user=user, date=target_date)
        consumed_water = sum(log.amount_ml for log in water_logs)
        
        # Goals
        goal_cals = float(profile.daily_calorie_goal) if profile and profile.daily_calorie_goal else 2000
        goal_protein = float(profile.protein_goal_g) if profile and profile.protein_goal_g else 120
        goal_carbs = float(profile.carbs_goal_g) if profile and profile.carbs_goal_g else 250
        goal_fat = float(profile.fat_goal_g) if profile and profile.fat_goal_g else 65
        
        data = {
            "date": target_date,
            "calories": {
                "consumed": consumed_cals,
                "goal": goal_cals,
                "remaining": round(goal_cals - consumed_cals, 2)
            },
            "protein": {
                "consumed": consumed_protein,
                "goal": goal_protein,
                "remaining": round(goal_protein - consumed_protein, 2)
            },
            "carbs": {
                "consumed": consumed_carbs,
                "goal": goal_carbs,
                "remaining": round(goal_carbs - consumed_carbs, 2)
            },
            "fat": {
                "consumed": consumed_fat,
                "goal": goal_fat,
                "remaining": round(goal_fat - consumed_fat, 2)
            },
            "water_ml": {
                "consumed": consumed_water,
                "goal": 2000
            },
            "meals_today": MealSerializer(meals, many=True).data
        }
        return Response(data)

class WeeklyMacrosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        seven_days_ago = today - timedelta(days=6)
        
        meals = Meal.objects.filter(user=user, date__range=[seven_days_ago, today]).order_by('date')
        
        # Group by date
        daily_stats: dict[str, dict] = {}
        for i in range(7):
            d = (seven_days_ago + timedelta(days=i)).isoformat()
            daily_stats[d] = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
            
        for meal in meals:
            d = meal.date.isoformat()
            if d in daily_stats:
                daily_stats[d]["calories"] += float(meal.total_calories)
                daily_stats[d]["protein"] += float(meal.total_protein)
                daily_stats[d]["carbs"] += float(meal.total_carbs)
                daily_stats[d]["fat"] += float(meal.total_fat)
                
        result = [{"date": k, **v} for k, v in daily_stats.items()]
        return Response(result)

class WeeklyWaterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        seven_days_ago = today - timedelta(days=6)
        
        logs = WaterLog.objects.filter(user=user, date__range=[seven_days_ago, today]).order_by('date')
        
        daily_water: dict[str, int] = {}
        for i in range(7):
            d = (seven_days_ago + timedelta(days=i)).isoformat()
            daily_water[d] = 0
            
        for log in logs:
            d = log.date.isoformat()
            if d in daily_water:
                daily_water[d] += log.amount_ml
                
        result = [{"date": k, "amount_ml": v} for k, v in daily_water.items()]
        return Response(result)

class WeightHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            limit = int(request.query_params.get('limit', 30))
        except (TypeError, ValueError):
            limit = 30
        limit = min(max(limit, 1), 365)
        
        logs = WeightLog.objects.filter(user=user).order_by('-date')[:limit]
        
        result = [{"date": log.date.isoformat(), "weight_kg": float(log.weight_kg)} for log in logs]
        result.reverse()
        return Response(result)
