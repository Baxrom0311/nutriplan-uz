from django.db import models
from django.conf import settings
from food.models import FoodItem

class Meal(models.Model):
    MEAL_TYPES = (
        ('breakfast', 'Breakfast'),
        ('morning_snack', 'Morning Snack'),
        ('lunch', 'Lunch'),
        ('snack', 'Snack'),
        ('dinner', 'Dinner'),
        ('evening_snack', 'Evening Snack'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meals')
    date = models.DateField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    
    # Calculated totals
    total_calories = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    total_protein = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total_carbs = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total_fat = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date', 'meal_type')
        ordering = ['-date', 'meal_type']

    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.meal_type}"

    def update_totals(self):
        items = self.items.all()
        self.total_calories = sum(item.calories for item in items)
        self.total_protein = sum(item.protein for item in items)
        self.total_carbs = sum(item.carbs for item in items)
        self.total_fat = sum(item.fat for item in items)
        self.save()

class MealItem(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    weight_g = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Calculated values for this specific weight
    calories = models.DecimalField(max_digits=7, decimal_places=2)
    protein = models.DecimalField(max_digits=6, decimal_places=2)
    carbs = models.DecimalField(max_digits=6, decimal_places=2)
    fat = models.DecimalField(max_digits=6, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.food_item.name} ({self.weight_g}g)"

    def save(self, *args, **kwargs):
        # Calculate nutritional values based on weight (per 100g base)
        from decimal import Decimal
        ratio = Decimal(str(self.weight_g)) / Decimal('100')
        self.calories = Decimal(str(self.food_item.calories_per_100g)) * ratio
        self.protein = Decimal(str(self.food_item.protein_per_100g)) * ratio
        self.carbs = Decimal(str(self.food_item.carbs_per_100g)) * ratio
        self.fat = Decimal(str(self.food_item.fat_per_100g)) * ratio
        
        super().save(*args, **kwargs)
        self.meal.update_totals()

    def delete(self, *args, **kwargs):
        meal = self.meal
        super().delete(*args, **kwargs)
        meal.update_totals()

class MealImageAnalysis(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meal_image_analyses')
    meal = models.ForeignKey(Meal, on_delete=models.SET_NULL, null=True, blank=True, related_name='image_analyses')
    meal_item = models.ForeignKey(MealItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='image_analyses')
    date = models.DateField()
    meal_type = models.CharField(max_length=20, choices=Meal.MEAL_TYPES)
    image = models.ImageField(upload_to='meal_photos/%Y/%m/%d/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    detected_food_name = models.CharField(max_length=200, blank=True)
    estimated_weight_g = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    estimated_calories = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    estimated_protein = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    estimated_carbs = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    estimated_fat = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    raw_response = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.detected_food_name or self.status}"

class WaterLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='water_logs')
    date = models.DateField()
    amount_ml = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.amount_ml}ml"

class WeightLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='weight_logs')
    date = models.DateField()
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.weight_kg}kg"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        # O'zgarishlar oxirgi vazn bo'lsa profilni yangilash
        latest_log = WeightLog.objects.filter(user=self.user).order_by('-date').first()
        
        super().save(*args, **kwargs)
        
        if not latest_log or self.date >= latest_log.date:
            profile = getattr(self.user, 'profile', None)
            if profile:
                profile.weight_kg = self.weight_kg
                profile.save() # recalculates nutrition
