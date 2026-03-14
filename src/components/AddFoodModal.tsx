import { useState, useEffect, useCallback } from "react";
import api from "@/lib/api";
import type { FoodItem, Meal, MealType } from "@/lib/types";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import { toast } from "sonner";

interface Props {
  open: boolean;
  mealType: MealType | null;
  date: string;
  existingMeals: Meal[];
  onClose: () => void;
  onAdded: () => void;
}

export default function AddFoodModal({ open, mealType, date, existingMeals, onClose, onAdded }: Props) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<FoodItem[]>([]);
  const [searching, setSearching] = useState(false);
  const [selected, setSelected] = useState<FoodItem | null>(null);
  const [weight, setWeight] = useState("100");
  const [submitting, setSubmitting] = useState(false);

  const search = useCallback(async (q: string) => {
    if (q.length < 2) { setResults([]); return; }
    setSearching(true);
    try {
      const { data } = await api.get(`/food/items/search/?search=${encodeURIComponent(q)}`);
      setResults(data.results || data);
    } catch {
      // silent
    } finally {
      setSearching(false);
    }
  }, []);

  useEffect(() => {
    const t = setTimeout(() => search(query), 300);
    return () => clearTimeout(t);
  }, [query, search]);

  useEffect(() => {
    if (!open) {
      setQuery("");
      setResults([]);
      setSelected(null);
      setWeight("100");
    }
  }, [open]);

  const preview = selected
    ? {
        cal: (parseFloat(selected.calories_per_100g || "0") * parseFloat(weight || "0")) / 100,
        protein: (parseFloat(selected.protein_per_100g || "0") * parseFloat(weight || "0")) / 100,
        carbs: (parseFloat(selected.carbs_per_100g || "0") * parseFloat(weight || "0")) / 100,
        fat: (parseFloat(selected.fat_per_100g || "0") * parseFloat(weight || "0")) / 100,
      }
    : null;

  const handleAdd = async () => {
    if (!selected || !mealType) return;
    setSubmitting(true);
    try {
      let mealId: number;
      const existing = existingMeals.find((m) => m.meal_type === mealType);
      if (existing) {
        mealId = existing.id;
      } else {
        const { data } = await api.post("/meals/", { date, meal_type: mealType });
        mealId = data.id;
      }
      await api.post(`/meals/${mealId}/items/`, { food_item: selected.id, weight_g: weight });
      toast.success("Qo'shildi!");
      onAdded();
      onClose();
    } catch {
      toast.error("Xatolik yuz berdi");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Ovqat qo'shish</DialogTitle>
        </DialogHeader>

        {!selected ? (
          <div className="space-y-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Ovqat qidirish..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="pl-9"
                autoFocus
              />
            </div>
            {searching && <p className="text-center text-sm text-muted-foreground">Qidirilmoqda...</p>}
            <div className="max-h-64 space-y-1 overflow-y-auto">
              {results.map((food) => (
                <button
                  key={food.id}
                  onClick={() => setSelected(food)}
                  className="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left text-sm transition-colors hover:bg-accent"
                >
                  <div>
                    <p className="font-medium">{food.name}</p>
                    {food.name_uz && food.name_uz !== food.name && (
                      <p className="text-xs text-muted-foreground">{food.name_uz}</p>
                    )}
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {Math.round(parseFloat(food.calories_per_100g || "0"))} kcal/100g
                  </span>
                </button>
              ))}
              {!searching && query.length >= 2 && results.length === 0 && (
                <p className="py-4 text-center text-sm text-muted-foreground">Hech narsa topilmadi</p>
              )}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <p className="font-medium">{selected.name}</p>
              <p className="text-xs text-muted-foreground">
                {Math.round(parseFloat(selected.calories_per_100g || "0"))} kcal / 100g
              </p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Gramm miqdori</label>
              <Input
                type="number"
                value={weight}
                onChange={(e) => setWeight(e.target.value)}
                min="1"
                autoFocus
              />
            </div>

            {preview && (
              <div className="grid grid-cols-4 gap-2 rounded-lg bg-muted p-3 text-center text-sm">
                <div>
                  <p className="font-semibold">{Math.round(preview.cal)}</p>
                  <p className="text-xs text-muted-foreground">kcal</p>
                </div>
                <div>
                  <p className="font-semibold text-protein">{Math.round(preview.protein)}</p>
                  <p className="text-xs text-muted-foreground">protein</p>
                </div>
                <div>
                  <p className="font-semibold text-carbs">{Math.round(preview.carbs)}</p>
                  <p className="text-xs text-muted-foreground">uglevodlar</p>
                </div>
                <div>
                  <p className="font-semibold text-fat">{Math.round(preview.fat)}</p>
                  <p className="text-xs text-muted-foreground">yog'</p>
                </div>
              </div>
            )}

            <div className="flex gap-2">
              <Button variant="outline" className="flex-1" onClick={() => setSelected(null)}>
                Orqaga
              </Button>
              <Button className="flex-1" onClick={handleAdd} disabled={submitting}>
                {submitting ? "Qo'shilmoqda..." : "Qo'shish"}
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
