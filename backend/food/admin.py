from django.contrib import admin
from .models import FoodCategory, FoodItem

@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_uz', 'created_at')
    search_fields = ('name', 'name_uz')

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_uz', 'category', 'calories_per_100g', 'is_verified')
    list_filter = ('category', 'source', 'is_verified', 'is_active')
    search_fields = ('name', 'name_uz', 'barcode', 'brand')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'name_uz', 'brand', 'barcode')
        }),
        ('Nutritional Values (per 100g)', {
            'fields': ('calories_per_100g', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g', 'fiber_per_100g', 'sugar_per_100g', 'sodium_per_100g')
        }),
        ('System Info', {
            'fields': ('source', 'external_id', 'image_url', 'is_verified', 'is_active', 'created_by')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        })
    )
