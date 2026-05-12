from django.core.management.base import BaseCommand
from food.models import FoodItem, FoodCategory

class Command(BaseCommand):
    help = 'Seeds the database with common food items'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding food items...')
        
        # Mapping for quickly getting categories
        categories = {}
        for cat in FoodCategory.objects.all():
            categories[cat.name] = cat
            
        common_foods = [
            # Fruits (pk=1)
            {"name": "Apple", "name_uz": "Olma", "cat": "Fruits", "cal": 52, "p": 0.3, "f": 0.2, "c": 14, "fib": 2.4, "s": 10},
            {"name": "Banana", "name_uz": "Banan", "cat": "Fruits", "cal": 89, "p": 1.1, "f": 0.3, "c": 23, "fib": 2.6, "s": 12},
            {"name": "Orange", "name_uz": "Apelsin", "cat": "Fruits", "cal": 47, "p": 0.9, "f": 0.1, "c": 12, "fib": 2.4, "s": 9},
            
            # Vegetables (pk=2)
            {"name": "Tomato", "name_uz": "Pomidor", "cat": "Vegetables", "cal": 18, "p": 0.9, "f": 0.2, "c": 3.9, "fib": 1.2, "s": 2.6},
            {"name": "Cucumber", "name_uz": "Bodring", "cat": "Vegetables", "cal": 15, "p": 0.7, "f": 0.1, "c": 3.6, "fib": 0.5, "s": 1.7},
            {"name": "Potato (boiled)", "name_uz": "Kartoshka (qaynatilgan)", "cat": "Vegetables", "cal": 87, "p": 1.9, "f": 0.1, "c": 20, "fib": 1.8, "s": 0.9},
            {"name": "Onion", "name_uz": "Piyoz", "cat": "Vegetables", "cal": 40, "p": 1.1, "f": 0.1, "c": 9.3, "fib": 1.7, "s": 4.2},
            {"name": "Carrot", "name_uz": "Sabzi", "cat": "Vegetables", "cal": 41, "p": 0.9, "f": 0.2, "c": 9.6, "fib": 2.8, "s": 4.7},
            
            # Meat & Poultry (pk=4)
            {"name": "Chicken Breast (raw)", "name_uz": "Tovuq to'shi (xom)", "cat": "Meat & Poultry", "cal": 165, "p": 31, "f": 3.6, "c": 0, "fib": 0, "s": 0},
            {"name": "Beef (lean)", "name_uz": "Mol go'shti (lahm)", "cat": "Meat & Poultry", "cal": 250, "p": 26, "f": 15, "c": 0, "fib": 0, "s": 0},
            {"name": "Lamb", "name_uz": "Qo'y go'shti", "cat": "Meat & Poultry", "cal": 294, "p": 25, "f": 21, "c": 0, "fib": 0, "s": 0},
            
            # Grains & Pasta (pk=3)
            {"name": "Rice (white, uncooked)", "name_uz": "Guruch (oq, xom)", "cat": "Grains & Pasta", "cal": 360, "p": 6.6, "f": 0.6, "c": 80, "fib": 1.3, "s": 0.1},
            {"name": "Bread (white)", "name_uz": "Non (oq)", "cat": "Grains & Pasta", "cal": 265, "p": 9, "f": 3.2, "c": 49, "fib": 2.7, "s": 5},
            {"name": "Oats", "name_uz": "Suli (Osyanka)", "cat": "Grains & Pasta", "cal": 389, "p": 16.9, "f": 6.9, "c": 66.3, "fib": 10.6, "s": 0},
            {"name": "Macaroni", "name_uz": "Makaron (xom)", "cat": "Grains & Pasta", "cal": 371, "p": 13, "f": 1.5, "c": 74, "fib": 3.2, "s": 2.6},
            
            # Dairy & Eggs (pk=6)
            {"name": "Egg (whole)", "name_uz": "Tuxum", "cat": "Dairy & Eggs", "cal": 155, "p": 13, "f": 11, "c": 1.1, "fib": 0, "s": 1.1},
            {"name": "Milk (whole, 3.25%)", "name_uz": "Sut (3.25%)", "cat": "Dairy & Eggs", "cal": 61, "p": 3.2, "f": 3.3, "c": 4.8, "fib": 0, "s": 5.1},
            {"name": "Cheese (Cheddar)", "name_uz": "Pishloq (Cheddar)", "cat": "Dairy & Eggs", "cal": 402, "p": 25, "f": 33, "c": 1.3, "fib": 0, "s": 0.5},
            {"name": "Yogurt (plain)", "name_uz": "Qatiq (oddiy)", "cat": "Dairy & Eggs", "cal": 61, "p": 3.5, "f": 3.3, "c": 4.7, "fib": 0, "s": 4.7},
            
            # Oils & Fats (pk=8)
            {"name": "Olive Oil", "name_uz": "Zaytun yog'i", "cat": "Oils & Fats", "cal": 884, "p": 0, "f": 100, "c": 0, "fib": 0, "s": 0},
            {"name": "Butter", "name_uz": "Sariyog'", "cat": "Oils & Fats", "cal": 717, "p": 0.9, "f": 81, "c": 0.1, "fib": 0, "s": 0.1},
            {"name": "Sunflower Oil", "name_uz": "Kungaboqar yog'i", "cat": "Oils & Fats", "cal": 884, "p": 0, "f": 100, "c": 0, "fib": 0, "s": 0},
            
            # Nuts & Seeds (pk=7)
            {"name": "Almonds", "name_uz": "Bodom", "cat": "Nuts & Seeds", "cal": 579, "p": 21, "f": 50, "c": 22, "fib": 12.5, "s": 4.4},
            {"name": "Walnuts", "name_uz": "Yong'oq", "cat": "Nuts & Seeds", "cal": 654, "p": 15, "f": 65, "c": 14, "fib": 6.7, "s": 2.6},
        ]
        
        count = 0
        for data in common_foods:
            cat = categories.get(data['cat'])
            if not cat:
                continue
                
            _, created = FoodItem.objects.get_or_create(
                name=data['name'],
                defaults={
                    'name_uz': data['name_uz'],
                    'category': cat,
                    'calories_per_100g': data['cal'],
                    'protein_per_100g': data['p'],
                    'fat_per_100g': data['f'],
                    'carbs_per_100g': data['c'],
                    'fiber_per_100g': data['fib'],
                    'sugar_per_100g': data['s'],
                    'source': 'manual'
                }
            )
            if created:
                count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {count} food items'))
