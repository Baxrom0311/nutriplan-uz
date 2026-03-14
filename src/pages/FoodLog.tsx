import { useState, useEffect, useCallback } from "react";
import api from "@/lib/api";
import type { Meal, MealType } from "@/lib/types";
import { MEAL_TYPE_LABELS } from "@/lib/types";
import AddFoodModal from "@/components/AddFoodModal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Trash2, ChevronLeft, ChevronRight } from "lucide-react";
import { toast } from "sonner";

const MEAL_TYPES: MealType[] = ["breakfast", "morning_snack", "lunch", "snack", "dinner", "evening_snack"];

export default function FoodLogPage() {
  const [date, setDate] = useState(() => new Date().toISOString().split("T")[0]);
  const [meals, setMeals] = useState<Meal[]>([]);
  const [loading, setLoading] = useState(true);
  const [foodModal, setFoodModal] = useState<{ open: boolean; mealType: MealType | null }>({ open: false, mealType: null });

  const fetchMeals = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get(`/meals/?date=${date}`);
      setMeals(data.results || data);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  }, [date]);

  useEffect(() => { fetchMeals(); }, [fetchMeals]);

  const shiftDate = (d: number) => {
    const dt = new Date(date);
    dt.setDate(dt.getDate() + d);
    setDate(dt.toISOString().split("T")[0]);
  };

  const deleteItem = async (itemId: number) => {
    try {
      await api.delete(`/meals/items/${itemId}/`);
      toast.success("O'chirildi");
      fetchMeals();
    } catch {
      toast.error("Xatolik");
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">Ovqat jurnali</h1>

      {/* Date picker */}
      <div className="flex items-center justify-center gap-3">
        <Button variant="outline" size="icon" onClick={() => shiftDate(-1)}>
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <Input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="w-40 text-center"
        />
        <Button variant="outline" size="icon" onClick={() => shiftDate(1)}>
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-10">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : (
        <div className="space-y-4">
          {MEAL_TYPES.map((type) => {
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
                    <Button size="sm" variant="outline" onClick={() => setFoodModal({ open: true, mealType: type })}>
                      <Plus className="h-3.5 w-3.5 mr-1" />
                      Qo'shish
                    </Button>
                  </div>
                </div>
                {meal && meal.items.length > 0 && (
                  <div className="mt-3 space-y-2 border-t pt-3">
                    {meal.items.map((item) => (
                      <div key={item.id} className="flex items-center justify-between text-sm">
                        <div>
                          <span className="font-medium">{item.food_item_detail?.name || "—"}</span>
                          <span className="ml-1 text-muted-foreground">({item.weight_g} g)</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-muted-foreground">{Math.round(parseFloat(item.calories || "0"))} kcal</span>
                          <button onClick={() => deleteItem(item.id)} className="text-muted-foreground hover:text-destructive">
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      <AddFoodModal
        open={foodModal.open}
        mealType={foodModal.mealType}
        date={date}
        existingMeals={meals}
        onClose={() => setFoodModal({ open: false, mealType: null })}
        onAdded={fetchMeals}
      />
    </div>
  );
}
