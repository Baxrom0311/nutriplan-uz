from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import datetime

from meals.models import Meal, MealItem, WaterLog, WeightLog
from food.models import FoodItem, FoodCategory

User = get_user_model()

class AnalyticsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='analytics_tester',
            email='analytics@example.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.today = datetime.date.today()
        
        # Profile goals
        self.profile = self.user.profile
        self.profile.weight_kg = 75
        self.profile.height_cm = 175
        self.profile.gender = 'male'
        self.profile.birth_date = datetime.date(1995, 1, 1)
        self.profile.activity_level = 'moderately_active'
        self.profile.goal = 'maintain_weight'
        self.profile.save()
        self.expected_goal = float(self.profile.daily_calorie_goal)

        # Create food and meal
        self.category = FoodCategory.objects.create(name='Snacks')
        self.food_item = FoodItem.objects.create(
            name='Banana', category=self.category,
            calories_per_100g=89, protein_per_100g=1.1,
            carbs_per_100g=22.8, fat_per_100g=0.3
        )
        self.meal = Meal.objects.create(user=self.user, date=self.today, meal_type='snack')
        
        # Add 100g Banana: 89 cals, 1.1 pro, 22.8 carbs, 0.3 fat
        MealItem.objects.create(meal=self.meal, food_item=self.food_item, weight_g=100)

        # Add 500ml Water
        WaterLog.objects.create(user=self.user, date=self.today, amount_ml=500)
        
        # Add 75kg weight
        WeightLog.objects.create(user=self.user, date=self.today, weight_kg=75.0)

    def test_dashboard_stats(self):
        res = self.client.get('/api/analytics/dashboard/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        data = res.data
        self.assertEqual(data['calories']['consumed'], 89.0)
        self.assertEqual(data['calories']['goal'], self.expected_goal)
        self.assertEqual(data['calories']['remaining'], round(self.expected_goal - 89.0, 2))
        
        self.assertEqual(data['water_ml']['consumed'], 500)
        self.assertEqual(len(data['meals_today']), 1)

    def test_weekly_macros(self):
        res = self.client.get('/api/analytics/weekly-macros/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 7)
        # Today's stats should match the banana
        today_stats = next(item for item in res.data if item['date'] == str(self.today))
        self.assertEqual(today_stats['calories'], 89.0)

    def test_weekly_water(self):
        res = self.client.get('/api/analytics/weekly-water/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 7)
        today_stats = next(item for item in res.data if item['date'] == str(self.today))
        self.assertEqual(today_stats['amount_ml'], 500)

    def test_weight_history(self):
        res = self.client.get('/api/analytics/weight-history/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data) >= 1)
        self.assertEqual(res.data[0]['weight_kg'], 75.0)
