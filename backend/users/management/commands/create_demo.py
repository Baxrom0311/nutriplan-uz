from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from food.models import FoodCategory, FoodItem
from meals.models import Meal, MealItem, WaterLog, WeightLog
from users.models import CustomUser


# O'zbek taomlari (100g uchun)
UZBEK_FOODS = [
    {"name": "Osh (palov)", "cat": "O'zbek taomlari", "cal": 210, "p": 8, "f": 9, "c": 25},
    {"name": "So'msa (go'shtli)", "cat": "O'zbek taomlari", "cal": 280, "p": 12, "f": 15, "c": 24},
    {"name": "Lag'mon", "cat": "O'zbek taomlari", "cal": 145, "p": 7, "f": 5, "c": 18},
    {"name": "Shashlik (mol go'shtli)", "cat": "O'zbek taomlari", "cal": 250, "p": 26, "f": 15, "c": 1},
    {"name": "Shurpa", "cat": "O'zbek taomlari", "cal": 85, "p": 5, "f": 3.5, "c": 8},
    {"name": "Manti", "cat": "O'zbek taomlari", "cal": 195, "p": 10, "f": 8, "c": 22},
    {"name": "Chuchvara", "cat": "O'zbek taomlari", "cal": 175, "p": 9, "f": 6, "c": 21},
    {"name": "Norin", "cat": "O'zbek taomlari", "cal": 165, "p": 11, "f": 6, "c": 18},
    {"name": "Qozon kabob", "cat": "O'zbek taomlari", "cal": 220, "p": 18, "f": 14, "c": 5},
    {"name": "Dimlama", "cat": "O'zbek taomlari", "cal": 120, "p": 7, "f": 5, "c": 12},
    {"name": "Non (o'zbek)", "cat": "O'zbek taomlari", "cal": 260, "p": 8, "f": 2, "c": 52},
    {"name": "Ko'k choy", "cat": "Ichimliklar", "cal": 1, "p": 0, "f": 0, "c": 0.2},
    {"name": "Qora choy", "cat": "Ichimliklar", "cal": 2, "p": 0, "f": 0, "c": 0.5},
    {"name": "Kompot", "cat": "Ichimliklar", "cal": 35, "p": 0.1, "f": 0, "c": 8.5},
    {"name": "Achichuk (salat)", "cat": "O'zbek taomlari", "cal": 25, "p": 1, "f": 0.2, "c": 5},
    {"name": "Suzma", "cat": "Sut mahsulotlari", "cal": 80, "p": 12, "f": 2, "c": 4},
    {"name": "Qatiq", "cat": "Sut mahsulotlari", "cal": 60, "p": 3.5, "f": 3.2, "c": 4.7},
    {"name": "Tuxum (qaynatilgan)", "cat": "Asosiy mahsulotlar", "cal": 155, "p": 13, "f": 11, "c": 1.1},
    {"name": "Banan", "cat": "Mevalar", "cal": 89, "p": 1.1, "f": 0.3, "c": 23},
    {"name": "Olma", "cat": "Mevalar", "cal": 52, "p": 0.3, "f": 0.2, "c": 14},
    {"name": "Yong'oq (aralash)", "cat": "Gazaklar", "cal": 607, "p": 20, "f": 54, "c": 20},
]

# 7 kunlik ovqat rejasi
DAILY_MEALS = [
    # Kun 0 (bugun)
    {
        "breakfast": [("Tuxum (qaynatilgan)", 120), ("Non (o'zbek)", 80), ("Ko'k choy", 300)],
        "lunch": [("Osh (palov)", 350), ("Achichuk (salat)", 150), ("Qora choy", 250)],
        "dinner": [("Shurpa", 400), ("Non (o'zbek)", 60)],
        "snack": [("Banan", 120), ("Qatiq", 200)],
    },
    # Kun 1
    {
        "breakfast": [("Suzma", 150), ("Non (o'zbek)", 100), ("Ko'k choy", 300)],
        "lunch": [("Lag'mon", 400), ("Achichuk (salat)", 120)],
        "dinner": [("Qozon kabob", 300), ("Non (o'zbek)", 70), ("Qora choy", 250)],
        "snack": [("Olma", 180), ("Yong'oq (aralash)", 30)],
    },
    # Kun 2
    {
        "breakfast": [("Tuxum (qaynatilgan)", 100), ("Non (o'zbek)", 90), ("Qatiq", 200)],
        "lunch": [("So'msa (go'shtli)", 250), ("Achichuk (salat)", 150), ("Kompot", 250)],
        "dinner": [("Dimlama", 400), ("Non (o'zbek)", 60)],
        "snack": [("Banan", 130)],
    },
    # Kun 3
    {
        "breakfast": [("Suzma", 120), ("Non (o'zbek)", 80), ("Ko'k choy", 300)],
        "lunch": [("Manti", 350), ("Achichuk (salat)", 130), ("Qora choy", 250)],
        "dinner": [("Shashlik (mol go'shtli)", 250), ("Non (o'zbek)", 70), ("Achichuk (salat)", 100)],
        "snack": [("Olma", 150), ("Qatiq", 180)],
    },
    # Kun 4
    {
        "breakfast": [("Tuxum (qaynatilgan)", 120), ("Non (o'zbek)", 70), ("Qora choy", 300)],
        "lunch": [("Osh (palov)", 300), ("Achichuk (salat)", 140), ("Ko'k choy", 250)],
        "dinner": [("Chuchvara", 350), ("Qatiq", 150)],
        "snack": [("Yong'oq (aralash)", 40), ("Banan", 100)],
    },
    # Kun 5
    {
        "breakfast": [("Suzma", 130), ("Non (o'zbek)", 90), ("Ko'k choy", 300)],
        "lunch": [("Norin", 400), ("Achichuk (salat)", 120)],
        "dinner": [("Shurpa", 380), ("Non (o'zbek)", 80)],
        "snack": [("Olma", 170), ("Qatiq", 200)],
    },
    # Kun 6
    {
        "breakfast": [("Tuxum (qaynatilgan)", 100), ("Non (o'zbek)", 100), ("Qatiq", 180)],
        "lunch": [("So'msa (go'shtli)", 200), ("Lag'mon", 250), ("Kompot", 250)],
        "dinner": [("Qozon kabob", 280), ("Achichuk (salat)", 130)],
        "snack": [("Banan", 110), ("Yong'oq (aralash)", 25)],
    },
]

DAILY_WATER = [2100, 1800, 2300, 2000, 1500, 2200, 1900]
DAILY_WEIGHTS = [82.5, 82.3, 82.4, 82.1, 82.0, 81.8, 81.6]


class Command(BaseCommand):
    help = 'Demo akkaunt yaratadi va 7 kunlik ma\'lumot bilan to\'ldiradi'

    def handle(self, *args, **kwargs):
        email = "demo@nutriplan.uz"
        password = "Demo2026!"

        # 1. Foydalanuvchi yaratish
        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={"username": "demo_user"}
        )
        if created:
            user.set_password(password)
            user.first_name = "Sardor"
            user.last_name = "Karimov"
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Foydalanuvchi yaratildi: {email}"))
        else:
            self.stdout.write(f"Foydalanuvchi mavjud: {email}")

        # 2. Profil to'ldirish
        profile = user.profile
        profile.gender = "male"
        profile.birth_date = date(1998, 5, 15)
        profile.height_cm = Decimal("178.00")
        profile.weight_kg = Decimal("82.50")
        profile.activity_level = "moderately_active"
        profile.goal = "lose_weight"
        profile.save()
        self.stdout.write(self.style.SUCCESS(
            f"Profil: {profile.daily_calorie_goal} kkal/kun, "
            f"BMR={profile.bmr}, TDEE={profile.tdee}"
        ))

        # 3. Kategoriyalar va ovqatlar yaratish
        categories = {}
        for food_data in UZBEK_FOODS:
            cat_name = food_data["cat"]
            if cat_name not in categories:
                cat, _ = FoodCategory.objects.get_or_create(name=cat_name)
                categories[cat_name] = cat

        food_items = {}
        for food_data in UZBEK_FOODS:
            item, _ = FoodItem.objects.get_or_create(
                name=food_data["name"],
                defaults={
                    "category": categories[food_data["cat"]],
                    "calories_per_100g": food_data["cal"],
                    "protein_per_100g": food_data["p"],
                    "fat_per_100g": food_data["f"],
                    "carbs_per_100g": food_data["c"],
                    "source": "manual",
                    "is_verified": True,
                }
            )
            food_items[food_data["name"]] = item

        self.stdout.write(self.style.SUCCESS(f"{len(food_items)} ta ovqat yaratildi"))

        # 4. Eski ma'lumotlarni o'chirish
        Meal.objects.filter(user=user).delete()
        WaterLog.objects.filter(user=user).delete()
        WeightLog.objects.filter(user=user).delete()

        today = date.today()

        # 5. 7 kunlik ovqat ma'lumotlari
        for day_offset in range(7):
            meal_date = today - timedelta(days=6 - day_offset)
            day_plan = DAILY_MEALS[day_offset]

            for meal_type, items in day_plan.items():
                meal = Meal.objects.create(
                    user=user,
                    date=meal_date,
                    meal_type=meal_type,
                )
                for food_name, weight_g in items:
                    food = food_items.get(food_name)
                    if food:
                        MealItem.objects.create(
                            meal=meal,
                            food_item=food,
                            weight_g=Decimal(str(weight_g)),
                        )

            self.stdout.write(f"  {meal_date}: ovqatlar kiritildi")

        # 6. Suv ma'lumotlari
        for day_offset in range(7):
            log_date = today - timedelta(days=6 - day_offset)
            total_ml = DAILY_WATER[day_offset]
            # 3-4 ta porsiyaga bo'lamiz
            portions = [250, 500, 250, total_ml - 1000]
            for ml in portions:
                if ml > 0:
                    WaterLog.objects.create(user=user, date=log_date, amount_ml=ml)

        self.stdout.write(self.style.SUCCESS("Suv ma'lumotlari kiritildi"))

        # 7. Vazn ma'lumotlari (30 kun)
        start_weight = 85.0
        for day_offset in range(30):
            log_date = today - timedelta(days=29 - day_offset)
            # Asta-sekin tushish (85 -> 81.6)
            progress = day_offset / 29
            weight = start_weight - (start_weight - 81.6) * progress
            # Biroz random tebranish
            weight += (day_offset % 3 - 1) * 0.2
            WeightLog.objects.create(
                user=user,
                date=log_date,
                weight_kg=Decimal(str(round(weight, 1))),
            )

        self.stdout.write(self.style.SUCCESS("Vazn tarixi kiritildi (30 kun)"))

        self.stdout.write(self.style.SUCCESS(
            f"\n{'='*50}\n"
            f"DEMO AKKAUNT TAYYOR!\n"
            f"Email: {email}\n"
            f"Parol: {password}\n"
            f"Maqsad: Vazn yo'qotish (85kg -> 81.6kg)\n"
            f"Kunlik kaloriya: {profile.daily_calorie_goal} kkal\n"
            f"{'='*50}"
        ))
