from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FoodCategory, FoodItem
from .serializers import (
    FoodCategorySerializer,
    FoodItemSerializer,
    FoodItemCreateSerializer,
    FoodItemSearchSerializer
)
from .openfoodfacts import OpenFoodFactsClient


class CanModifyFoodItem(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated

        return request.user.is_staff or obj.created_by_id == request.user.id

class FoodCategoryListView(generics.ListAPIView):
    queryset = FoodCategory.objects.order_by('name')
    serializer_class = FoodCategorySerializer
    permission_classes = [AllowAny]

    @method_decorator(cache_page(60 * 60)) # Cache for 1 hour
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class FoodItemListCreateView(generics.ListCreateAPIView):
    queryset = FoodItem.objects.filter(is_active=True).select_related('category').order_by('name')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FoodItemCreateSerializer
        return FoodItemSerializer

class FoodItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FoodItem.objects.select_related('category')
    permission_classes = [IsAuthenticated, CanModifyFoodItem]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return FoodItemCreateSerializer
        return FoodItemSerializer

class FoodItemSearchView(generics.ListAPIView):
    serializer_class = FoodItemSearchSerializer
    permission_classes = [IsAuthenticated]
    
    @method_decorator(cache_page(60 * 5)) # Cache for 5 minutes
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        query = self.request.GET.get('search', '') or self.request.GET.get('q', '')
        category_id = self.request.GET.get('category')
        
        queryset = FoodItem.objects.filter(is_active=True).select_related('category').order_by('name')
        
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(name_uz__icontains=query))
            
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        return queryset[:50] # Limit results

class FoodItemBarcodeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, barcode):
        # 1. Baza dan qidirish
        item = FoodItem.objects.filter(barcode=barcode).first()
        
        if item:
            serializer = FoodItemSerializer(item)
            return Response(serializer.data)
            
        # 2. Agar topilmasa, OpenFoodFacts API dan olib kelish
        client = OpenFoodFactsClient()
        new_item = client.import_to_db(barcode, request.user)
        
        if new_item:
            serializer = FoodItemSerializer(new_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

class ImportFromOpenFoodFactsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        barcode = request.data.get('barcode')
        if not barcode:
            return Response({"barcode": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
            
        client = OpenFoodFactsClient()
        item = client.import_to_db(barcode, request.user)
        
        if item:
            serializer = FoodItemSerializer(item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response({"detail": "Could not import product. It may not exist in OpenFoodFacts database."}, 
                        status=status.HTTP_404_NOT_FOUND)
