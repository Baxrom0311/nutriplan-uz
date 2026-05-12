import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from food.models import FoodCategory, FoodItem

def populate():
    print("O'zbek taomlari qo'shilmoqda...")
    
    cat_taom, _ = FoodCategory.objects.get_or_create(name='Main Courses', name_uz='Asosiy taomlar', icon='🍲')
    cat_meva, _ = FoodCategory.objects.get_or_create(name='Fruits', name_uz='Mevalar', icon='🍎')
    cat_ichimlik, _ = FoodCategory.objects.get_or_create(name='Beverages', name_uz='Ichimliklar', icon='🥤')
    
    foods = [
        # Taomlar
        {"name": "Palov (Osh)", "name_uz": "Palov (Osh)", "category": cat_taom, "cal": 180, "protein": 5.5, "carbs": 24.1, "fat": 6.8},
        {"name": "Manti", "name_uz": "Manti", "category": cat_taom, "cal": 220, "protein": 8.0, "carbs": 25.0, "fat": 10.0},
        {"name": "Somsa", "name_uz": "Somsa", "category": cat_taom, "cal": 300, "protein": 9.5, "carbs": 32.0, "fat": 15.2},
        {"name": "Lag'mon", "name_uz": "Lag'mon", "category": cat_taom, "cal": 150, "protein": 5.0, "carbs": 20.0, "fat": 5.5},
        {"name": "Shashlik (Qo'y go'shti)", "name_uz": "Shashlik (Qo'y go'shti)", "category": cat_taom, "cal": 250, "protein": 18.0, "carbs": 1.0, "fat": 20.0},
        {"name": "Non (Uy noni)", "name_uz": "Non (Uy noni)", "category": cat_taom, "cal": 270, "protein": 8.0, "carbs": 53.0, "fat": 1.5},
        {"name": "Norin", "name_uz": "Norin", "category": cat_taom, "cal": 280, "protein": 12.0, "carbs": 28.0, "fat": 13.0},
        
        # Mevalar/Sabzavotlar
        {"name": "Olma", "name_uz": "Olma", "category": cat_meva, "cal": 52, "protein": 0.3, "carbs": 13.8, "fat": 0.2},
        {"name": "Banan", "name_uz": "Banan", "category": cat_meva, "cal": 89, "protein": 1.1, "carbs": 22.8, "fat": 0.3},
        {"name": "Uzum", "name_uz": "Uzum", "category": cat_meva, "cal": 69, "protein": 0.7, "carbs": 18.1, "fat": 0.2},
        {"name": "Qovun", "name_uz": "Qovun", "category": cat_meva, "cal": 34, "protein": 0.8, "carbs": 8.2, "fat": 0.2},
        {"name": "Tarpuz", "name_uz": "Tarbuz", "category": cat_meva, "cal": 30, "protein": 0.6, "carbs": 7.6, "fat": 0.2},
        
        # Ichimliklar
        {"name": "Qora choy (shakarsiz)", "name_uz": "Qora choy (shakarsiz)", "category": cat_ichimlik, "cal": 2, "protein": 0.1, "carbs": 0.5, "fat": 0.0},
        {"name": "Ko'k choy (shakarsiz)", "name_uz": "Ko'k choy (shakarsiz)", "category": cat_ichimlik, "cal": 2, "protein": 0.1, "carbs": 0.0, "fat": 0.0},
        {"name": "Kola (Coca-Cola)", "name_uz": "Kola (Coca-Cola)", "category": cat_ichimlik, "cal": 42, "protein": 0.0, "carbs": 10.6, "fat": 0.0},
    ]

    count = 0
    for f in foods:
        item, created = FoodItem.objects.get_or_create(
            name=f["name"],
            defaults={
                "name_uz": f["name_uz"],
                "category": f["category"],
                "calories_per_100g": f["cal"],
                "protein_per_100g": f["protein"],
                "carbs_per_100g": f["carbs"],
                "fat_per_100g": f["fat"],
                "is_verified": True
            }
        )
        if created:
            count += 1

    print(f"Baza tayyor! {count} ta yangi taom qo'shildi.")

if __name__ == '__main__':
    populate()
