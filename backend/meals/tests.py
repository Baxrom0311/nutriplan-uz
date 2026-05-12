from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import datetime
from PIL import Image
from food.models import FoodItem, FoodCategory
from meals.ai_analysis import FoodVisionResult
from meals.models import Meal, MealImageAnalysis, MealItem, WaterLog, WeightLog

User = get_user_model()

class MealsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='meal_tester',
            email='meal@example.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.category = FoodCategory.objects.create(name='Fruits')
        self.food_item = FoodItem.objects.create(
            name='Apple', category=self.category,
            calories_per_100g=52, protein_per_100g=0.3,
            carbs_per_100g=14, fat_per_100g=0.2
        )
        
        self.today = datetime.date.today()
        self.meal = Meal.objects.create(
            user=self.user,
            date=self.today,
            meal_type='breakfast'
        )

    def test_meal_list_create(self):
        data = {
            'date': str(self.today),
            'meal_type': 'lunch'
        }
        res = self.client.post('/api/meals/', data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Meal.objects.filter(meal_type='lunch').exists())

    def test_add_meal_item(self):
        data = {
            'food_item': self.food_item.id,
            'weight_g': 200
        }
        # 200g apple -> 104 kcal, 0.6g protein, 28g carbs, 0.4g fat
        res = self.client.post(f'/api/meals/{self.meal.id}/items/', data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        # Meal totals should auto-update
        self.meal.refresh_from_db()
        self.assertEqual(self.meal.total_calories, 104)

    def test_negative_meal_item_weight_rejected(self):
        res = self.client.post(f'/api/meals/{self.meal.id}/items/', {
            'food_item': self.food_item.id,
            'weight_g': -50
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_water_log_create(self):
        first_res = self.client.post('/api/meals/water/', {
            'date': str(self.today),
            'amount_ml': 500
        })
        second_res = self.client.post('/api/meals/water/', {
            'date': str(self.today),
            'amount_ml': 250
        })

        self.assertEqual(first_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WaterLog.objects.filter(user=self.user, date=self.today).count(), 2)

    def test_negative_water_log_rejected(self):
        res = self.client.post('/api/meals/water/', {
            'date': str(self.today),
            'amount_ml': -500
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weight_log_create(self):
        data = {
            'date': str(self.today),
            'weight_kg': 75.5
        }
        res = self.client.post('/api/meals/weight/', data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WeightLog.objects.filter(user=self.user).first().weight_kg, 75.50)

    def test_negative_weight_log_rejected(self):
        res = self.client.post('/api/meals/weight/', {
            'date': str(self.today),
            'weight_kg': -75.5
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def _sample_upload(self):
        buffer = BytesIO()
        image = Image.new('RGB', (32, 32), color='white')
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        return SimpleUploadedFile('meal.jpg', buffer.read(), content_type='image/jpeg')

    @patch('meals.views.analyze_meal_photo')
    def test_photo_analysis_creates_meal_item(self, analyze_mock):
        analyze_mock.return_value = FoodVisionResult(
            food_name='Osh',
            estimated_weight_g=Decimal('350'),
            calories=Decimal('735'),
            protein=Decimal('28'),
            carbs=Decimal('87'),
            fat=Decimal('31'),
            confidence=Decimal('0.82'),
            notes_uz='Taxminiy osh porsiyasi',
            raw={'food_name': 'Osh'},
        )

        res = self.client.post('/api/meals/photo-analyze/', {
            'date': str(self.today),
            'meal_type': 'lunch',
            'image': self._sample_upload(),
        }, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['status'], 'processed')
        self.assertEqual(res.data['detected_food_name'], 'Osh')
        self.assertTrue(MealImageAnalysis.objects.filter(user=self.user, detected_food_name='Osh').exists())
        self.assertTrue(Meal.objects.filter(user=self.user, date=self.today, meal_type='lunch').exists())
        self.assertTrue(MealItem.objects.filter(meal__user=self.user, food_item__name='Osh').exists())
