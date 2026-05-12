from datetime import date

def get_age_from_birthdate(birth_date) -> int:
    if not birth_date:
        return 25
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def calculate_bmr_mifflin(weight_kg, height_cm, age, gender) -> float:
    base = (10 * float(weight_kg)) + (6.25 * float(height_cm)) - (5 * age)
    if gender == 'male':
        return base + 5
    else:
        return base - 161

def calculate_bmr_harris(weight_kg, height_cm, age, gender) -> float:
    if gender == 'male':
        return 88.362 + (13.397 * float(weight_kg)) + (4.799 * float(height_cm)) - (5.677 * age)
    else:
        return 447.593 + (9.247 * float(weight_kg)) + (3.098 * float(height_cm)) - (4.330 * age)

ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,
    'lightly_active': 1.375,
    'moderately_active': 1.55,
    'very_active': 1.725,
    'extra_active': 1.9,
}

def calculate_tdee(bmr, activity_level) -> float:
    if not activity_level or activity_level not in ACTIVITY_MULTIPLIERS:
        activity_level = 'sedentary'
    return bmr * ACTIVITY_MULTIPLIERS[activity_level]

def calculate_daily_goal(tdee, goal) -> int:
    adjustments = {
        'lose_weight': -500,
        'maintain_weight': 0,
        'gain_weight': 300,
    }
    if not goal or goal not in adjustments:
        goal = 'maintain_weight'
    return int(tdee + adjustments[goal])

def calculate_macros(daily_calories, goal, weight_kg) -> dict:
    protein_per_kg = {
        'lose_weight': 2.0,
        'maintain_weight': 1.6,
        'gain_weight': 1.8,
    }
    
    if not goal or goal not in protein_per_kg:
        goal = 'maintain_weight'
        
    protein_g = float(weight_kg) * protein_per_kg[goal]
    fat_g = (daily_calories * 0.25) / 9
    remaining_cals = daily_calories - (protein_g * 4) - (fat_g * 9)
    carbs_g = remaining_cals / 4
    
    return {
        'protein_g': round(protein_g, 2),
        'fat_g': round(fat_g, 2),
        'carbs_g': round(carbs_g, 2),
    }

def recalculate_user_nutrition(profile):
    if profile.weight_kg and profile.height_cm and profile.birth_date and profile.gender:
        age = get_age_from_birthdate(profile.birth_date)
        profile.bmr = calculate_bmr_mifflin(profile.weight_kg, profile.height_cm, age, profile.gender)
        profile.tdee = calculate_tdee(profile.bmr, profile.activity_level)
        profile.daily_calorie_goal = calculate_daily_goal(profile.tdee, profile.goal)
        
        macros = calculate_macros(profile.daily_calorie_goal, profile.goal, profile.weight_kg)
        profile.protein_goal_g = macros['protein_g']
        profile.fat_goal_g = macros['fat_g']
        profile.carbs_goal_g = macros['carbs_g']
    else:
        profile.bmr = None
        profile.tdee = None
        profile.daily_calorie_goal = None
        profile.protein_goal_g = None
        profile.fat_goal_g = None
        profile.carbs_goal_g = None
