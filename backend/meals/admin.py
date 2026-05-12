from django.contrib import admin
from .models import Meal, MealItem, WaterLog, WeightLog

class MealItemInline(admin.TabularInline):
    model = MealItem
    extra = 1

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'meal_type', 'total_calories')
    list_filter = ('date', 'meal_type')
    search_fields = ('user__email',)
    inlines = [MealItemInline]
    readonly_fields = ('total_calories', 'total_protein', 'total_carbs', 'total_fat', 'created_at', 'updated_at')

@admin.register(WaterLog)
class WaterLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'amount_ml')
    list_filter = ('date',)
    search_fields = ('user__email',)

@admin.register(WeightLog)
class WeightLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'weight_kg')
    list_filter = ('date',)
    search_fields = ('user__email',)
