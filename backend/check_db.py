import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development'))
django.setup()

from food.models import FoodItem, FoodCategory

print("Total foods:", FoodItem.objects.count())
print("Total categories:", FoodCategory.objects.count())
