from django.urls import path
from .views import (
    FoodCategoryListView,
    FoodItemListCreateView,
    FoodItemDetailView,
    FoodItemSearchView,
    FoodItemBarcodeView,
    ImportFromOpenFoodFactsView
)

urlpatterns = [
    path('categories/', FoodCategoryListView.as_view(), name='food-category-list'),
    path('items/', FoodItemListCreateView.as_view(), name='food-item-list-create'),
    path('items/<int:pk>/', FoodItemDetailView.as_view(), name='food-item-detail'),
    path('items/search/', FoodItemSearchView.as_view(), name='food-item-search'),
    path('items/barcode/<str:barcode>/', FoodItemBarcodeView.as_view(), name='food-item-barcode'),
    path('openfoodfacts/', ImportFromOpenFoodFactsView.as_view(), name='food-import-openfoodfacts'),
]
