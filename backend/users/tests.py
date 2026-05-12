from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import UserProfile

User = get_user_model()

import datetime

class UsersAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpassword123'
        )
        self.profile = self.user.profile
        self.profile.weight_kg = 80
        self.profile.height_cm = 180
        self.profile.gender = 'male'
        self.profile.birth_date = datetime.date(1995, 1, 1)
        self.profile.activity_level = 'moderately_active'
        self.profile.goal = 'lose_weight'
        self.profile.save()

    def test_user_registration(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123',
            'password2': 'newpassword123'
        }
        res = self.client.post('/api/auth/register/', data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_user_login(self):
        res = self.client.post('/api/auth/login/', {'email': 'test@example.com', 'password': 'testpassword123'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_profile_retrieval(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/auth/me/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['weight_kg'], '80.00')

    def test_nutrition_recalculation(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post('/api/auth/me/calculate/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # BMR should be populated now
        self.assertIsNotNone(res.data['bmr'])
        self.assertIsNotNone(res.data['daily_calorie_goal'])

    def test_change_password_rejects_weak_password(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post('/api/auth/password/reset/', {
            'old_password': 'testpassword123',
            'new_password': '123',
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('123'))
