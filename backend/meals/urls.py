from django.urls import path
from .views import (
    MealListCreateView,
    MealDetailView,
    MealImageAnalyzeView,
    MealItemCreateView,
    MealItemDetailView,
    WaterLogListCreateView,
    WaterLogDetailView,
    WeightLogListCreateView,
    WeightLogDetailView
)

urlpatterns = [
    path('', MealListCreateView.as_view(), name='meal-list-create'),
    path('<int:pk>/', MealDetailView.as_view(), name='meal-detail'),
    
    path('<int:meal_pk>/items/', MealItemCreateView.as_view(), name='meal-item-create'),
    path('items/<int:pk>/', MealItemDetailView.as_view(), name='meal-item-detail'),
    path('photo-analyze/', MealImageAnalyzeView.as_view(), name='meal-photo-analyze'),
    
    path('water/', WaterLogListCreateView.as_view(), name='water-log-list-create'),
    path('water/<int:pk>/', WaterLogDetailView.as_view(), name='water-log-detail'),
    
    path('weight/', WeightLogListCreateView.as_view(), name='weight-log-list-create'),
    path('weight/<int:pk>/', WeightLogDetailView.as_view(), name='weight-log-detail'),
]
