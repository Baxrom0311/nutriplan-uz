from django.db import models
from django.conf import settings

class FoodCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    name_uz = models.CharField(max_length=100, null=True, blank=True)
    icon = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class FoodItem(models.Model):
    SOURCE_CHOICES = (
        ('manual', 'Manual'),
        ('openfoodfacts', 'Open Food Facts'),
        ('usda', 'USDA'),
    )

    category = models.ForeignKey(FoodCategory, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    name_uz = models.CharField(max_length=200, null=True, blank=True)
    barcode = models.CharField(max_length=50, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    
    # 100g uchun ozuqaviy qiymat
    calories_per_100g = models.DecimalField(max_digits=7, decimal_places=2)
    protein_per_100g = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    carbs_per_100g = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fat_per_100g = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fiber_per_100g = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    sugar_per_100g = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    sodium_per_100g = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='manual')
    external_id = models.CharField(max_length=100, null=True, blank=True)
    
    image_url = models.URLField(max_length=500, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['barcode']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.name
