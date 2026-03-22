import { useState, useEffect, useCallback } from "react";
import api from "@/lib/api";
import type { Meal, WaterLog, MealType } from "@/lib/types";
import { MEAL_TYPE_LABELS } from "@/lib/types";
import { useAuthStore } from "@/stores/authStore";
import CalorieRing from "@/components/CalorieRing";
import MacroBar from "@/components/MacroBar";
import AddFoodModal from "@/components/AddFoodModal";
import { Button } from "@/components/ui/button";
import { getTodayDateInputValue } from "@/lib/date";
import { Plus, Droplets, Trash2 } from "lucide-react";
import { toast } from "sonner";

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const fetchProfile = useAuthStore((s) => s.fetchProfile);
  const [meals, setMeals] = useState<Meal[]>([]);
  const [water, setWater] = useState<WaterLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [foodModal, setFoodModal] = useState<{ open: boolean; mealType: MealType | null }>({ open: false, mealType: null });

  const fetchData = useCallback(async () => {
    try {
      const [mealsRes, waterRes] = await Promise.all([
        api.get(`/meals/?date=${getTodayDateInputValue()}`),
        api.get(`/meals/water/?date=${getTodayDateInputValue()}`),
      ]);
      setMeals(mealsRes.data.results || mealsRes.data);
      setWater(Array.isArray(waterRes.data) ? waterRes.data : waterRes.data.results || []);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProfile();
    fetchData();
  }, [fetchData, fetchProfile]);

  const totalCal = meals.reduce((s, m) => s + parseFloat(m.total_calories || "0"), 0);
  const totalProtein = meals.reduce((s, m) => s + parseFloat(m.total_protein || "0"), 0);
  const totalCarbs = meals.reduce((s, m) => s + parseFloat(m.total_carbs || "0"), 0);
  const totalFat = meals.reduce((s, m) => s + parseFloat(m.total_fat || "0"), 0);
  const totalWater = water.reduce((s, w) => s + w.amount_ml, 0);

  const addWater = async (ml: number) => {
    try {
      await api.post("/meals/water/", { date: getTodayDateInputValue(), amount_ml: ml });
      fetchData();
      toast.success(`+${ml} ml suv qo'shildi`);
    } catch {
      toast.error("Xatolik yuz berdi");
    }
  };

  const deleteWater = async (id: number) => {
    try {
      await api.delete(`/meals/water/${id}/`);
      fetchData();
    } catch {
      toast.error("Xatolik");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const mealTypes: MealType[] = ["breakfast", "morning_snack", "lunch", "snack", "dinner", "evening_snack"];

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">Bugungi natijalar</h1>

      {/* Calorie Ring */}
      <div className="flex justify-center rounded-xl border bg-card p-6">
        <CalorieRing consumed={Math.round(totalCal)} goal={user?.daily_calorie_goal || 2000} />
      </div>

      {/* Macros */}
      <div className="space-y-3 rounded-xl border bg-card p-5">
        <h2 className="text-sm font-semibold text-muted-foreground">Makronutrientlar</h2>
        <MacroBar label="Protein" consumed={Math.round(totalProtein)} goal={parseFloat(user?.protein_goal_g || "0")} color="hsl(217,91%,60%)" />
        <MacroBar label="Uglevodlar" consumed={Math.round(totalCarbs)} goal={parseFloat(user?.carbs_goal_g || "0")} color="hsl(25,95%,53%)" />
        <MacroBar label="Yog'" consumed={Math.round(totalFat)} goal={parseFloat(user?.fat_goal_g || "0")} color="hsl(48,96%,53%)" />
      </div>

      {/* Today's Meals */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-muted-foreground">Bugungi ovqatlar</h2>
        {mealTypes.map((type) => {
          const meal = meals.find((m) => m.meal_type === type);
          return (
            <div key={type} className="rounded-xl border bg-card p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{MEAL_TYPE_LABELS[type].en}</p>
                  <p className="text-xs text-muted-foreground">{MEAL_TYPE_LABELS[type].uz}</p>
                </div>
                <div className="flex items-center gap-2">
                  {meal && (
                    <span className="text-sm font-semibold text-primary">
                      {Math.round(parseFloat(meal.total_calories || "0"))} kcal
                    </span>
                  )}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setFoodModal({ open: true, mealType: type })}
                  >
                    <Plus className="h-3.5 w-3.5" />
                    Qo'shish
                  </Button>
                </div>
              </div>
              {meal && meal.items.length > 0 && (
                <div className="mt-3 space-y-1.5 border-t pt-3">
                  {meal.items.map((item) => (
                    <div key={item.id} className="flex items-center justify-between text-sm">
                      <span className="text-foreground">
                        {item.food_item_detail?.name || "—"}{" "}
                        <span className="text-muted-foreground">({item.weight_g} g)</span>
                      </span>
                      <span className="text-muted-foreground">{Math.round(parseFloat(item.calories || "0"))} kcal</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Water */}
      <div className="rounded-xl border bg-card p-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Droplets className="h-5 w-5 text-water" />
            <h2 className="font-semibold">Suv</h2>
          </div>
          <span className="text-lg font-bold">{totalWater} ml</span>
        </div>
        <div className="mt-3 flex gap-2">
          {[250, 500, 1000].map((ml) => (
            <Button key={ml} variant="outline" size="sm" onClick={() => addWater(ml)}>
              +{ml} ml
            </Button>
          ))}
        </div>
        {water.length > 0 && (
          <div className="mt-3 space-y-1 border-t pt-3">
            {water.map((w) => (
              <div key={w.id} className="flex items-center justify-between text-sm">
                <span>{w.amount_ml} ml</span>
                <button onClick={() => deleteWater(w.id)} className="text-muted-foreground hover:text-destructive">
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <AddFoodModal
        open={foodModal.open}
        mealType={foodModal.mealType}
        date={getTodayDateInputValue()}
        existingMeals={meals}
        onClose={() => setFoodModal({ open: false, mealType: null })}
        onAdded={fetchData}
      />
    </div>
  );
}
