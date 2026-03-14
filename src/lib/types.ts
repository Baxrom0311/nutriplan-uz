export interface UserProfile {
  gender: "male" | "female";
  birth_date: string;
  height_cm: string;
  weight_kg: string;
  activity_level: "sedentary" | "lightly_active" | "moderately_active" | "very_active" | "extra_active";
  goal: "lose_weight" | "maintain_weight" | "gain_weight";
  bmr: string;
  tdee: string;
  daily_calorie_goal: number;
  protein_goal_g: string;
  carbs_goal_g: string;
  fat_goal_g: string;
  avatar: string;
  is_premium: boolean;
}

export interface FoodItem {
  id: number;
  category_name: string;
  category_name_uz: string;
  name: string;
  name_uz: string;
  barcode: string;
  brand: string;
  calories_per_100g: string;
  protein_per_100g: string;
  carbs_per_100g: string;
  fat_per_100g: string;
  fiber_per_100g: string;
  sugar_per_100g: string;
  sodium_per_100g: string;
  source: "manual" | "openfoodfacts" | "usda";
  image_url: string;
  is_verified: boolean;
}

export interface MealItem {
  id: number;
  meal: number;
  food_item: number;
  food_item_detail: FoodItem;
  weight_g: string;
  calories: string;
  protein: string;
  carbs: string;
  fat: string;
  created_at: string;
}

export interface Meal {
  id: number;
  user: number;
  date: string;
  meal_type: MealType;
  total_calories: string;
  total_protein: string;
  total_carbs: string;
  total_fat: string;
  items: MealItem[];
  created_at: string;
}

export type MealType = "breakfast" | "morning_snack" | "lunch" | "snack" | "dinner" | "evening_snack";

export interface WaterLog {
  id: number;
  date: string;
  amount_ml: number;
  created_at: string;
  user: number;
}

export interface WeightLog {
  id: number;
  date: string;
  weight_kg: string;
  notes: string;
  created_at: string;
  user: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const MEAL_TYPE_LABELS: Record<MealType, { en: string; uz: string }> = {
  breakfast: { en: "Breakfast", uz: "Nonushta" },
  morning_snack: { en: "Morning Snack", uz: "Tushlik oldi gazak" },
  lunch: { en: "Lunch", uz: "Tushlik" },
  snack: { en: "Snack", uz: "Gazak" },
  dinner: { en: "Dinner", uz: "Kechki ovqat" },
  evening_snack: { en: "Evening Snack", uz: "Kechki gazak" },
};

export const ACTIVITY_LABELS: Record<string, string> = {
  sedentary: "Kam harakatli (ofis ishi)",
  lightly_active: "Hafta 1-3 kun sport",
  moderately_active: "Hafta 3-5 kun sport",
  very_active: "Hafta 6-7 kun sport",
  extra_active: "Og'ir jismoniy ish",
};

export const GOAL_LABELS: Record<string, string> = {
  lose_weight: "Vazn yo'qotish",
  maintain_weight: "Vaznni saqlash",
  gain_weight: "Vazn olish",
};
