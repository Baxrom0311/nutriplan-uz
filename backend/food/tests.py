from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from food.models import FoodCategory, FoodItem

User = get_user_model()

class FoodAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='food_tester',
            email='food@example.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.category = FoodCategory.objects.create(
            name='Fruits',
            name_uz='Mevalar'
        )
        self.food_item = FoodItem.objects.create(
            name='Apple',
            name_uz='Olma',
            category=self.category,
            calories_per_100g=52,
            protein_per_100g=0.3,
            carbs_per_100g=14,
            fat_per_100g=0.2,
            barcode='123456789'
        )

    def test_category_list(self):
        res = self.client.get('/api/food/categories/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Should contain at least the created category
        self.assertTrue(len(res.data) >= 1)

    def test_food_search(self):
        res = self.client.get('/api/food/items/search/?q=Olma')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Assuming pagination or result list, we check if one result matched
        self.assertTrue(len(res.data) >= 1)
        
    def test_food_barcode_search(self):
        # We search an existing item by barcode
        res = self.client.get('/api/food/items/barcode/123456789/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], 'Apple')

    def test_food_create(self):
        data = {
            'name': 'Banana',
            'name_uz': 'Banan',
            'category': self.category.id,
            'calories_per_100g': 89,
            'protein_per_100g': 1.1,
            'carbs_per_100g': 22.8,
            'fat_per_100g': 0.3
        }
        res = self.client.post('/api/food/items/', data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(FoodItem.objects.filter(name='Banana').exists())

    def test_other_user_cannot_update_shared_food_item(self):
        other_user = User.objects.create_user(
            username='other_user',
            email='other@example.com',
            password='testpassword123'
        )
        client = APIClient()
        client.force_authenticate(user=other_user)

        res = client.patch(f'/api/food/items/{self.food_item.id}/', {'name': 'Hacked Apple'})

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.food_item.refresh_from_db()
        self.assertEqual(self.food_item.name, 'Apple')
