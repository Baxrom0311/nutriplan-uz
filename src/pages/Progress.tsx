import { useState, useEffect } from "react";
import api from "@/lib/api";
import type { WeightLog } from "@/lib/types";
import { useAuthStore } from "@/stores/authStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from "recharts";
import { Plus, Activity, Flame } from "lucide-react";
import { toast } from "sonner";

export default function ProgressPage() {
  const user = useAuthStore((s) => s.user);
  const [weights, setWeights] = useState<WeightLog[]>([]);
  const [weeklyMacros, setWeeklyMacros] = useState<any[]>([]);
  const [weeklyWater, setWeeklyWater] = useState<any[]>([]);
  const [weightModal, setWeightModal] = useState(false);
  const [newWeight, setNewWeight] = useState("");
  const [newDate, setNewDate] = useState(() => new Date().toISOString().split("T")[0]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get("/meals/weight/"),
      api.get("/analytics/weekly-macros/"),
      api.get("/analytics/weekly-water/"),
    ])
      .then(([w, m, wa]) => {
        setWeights(w.data.results || w.data);
        setWeeklyMacros(m.data.results || m.data);
        setWeeklyWater(wa.data.results || wa.data);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const addWeight = async () => {
    if (!newWeight) return;
    try {
      await api.post("/meals/weight/", { date: newDate, weight_kg: newWeight });
      toast.success("Vazn saqlandi");
      setWeightModal(false);
      const { data } = await api.get("/meals/weight/");
      setWeights(data.results || data);
    } catch {
      toast.error("Xatolik");
    }
  };

  const weightData = (Array.isArray(weights) ? weights : [])
    .slice()
    .sort((a, b) => a.date.localeCompare(b.date))
    .map((w) => ({ date: w.date.slice(5), kg: parseFloat(w.weight_kg) }));

  const macroData = (Array.isArray(weeklyMacros) ? weeklyMacros : []).map((d: any) => ({
    date: (d.date || "").slice(5),
    calories: Math.round(parseFloat(d.calories || d.total_calories || "0")),
  }));

  const waterData = (Array.isArray(weeklyWater) ? weeklyWater : []).map((d: any) => ({
    date: (d.date || "").slice(5),
    ml: d.amount_ml || d.total_ml || 0,
  }));

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">Progress</h1>

      {/* Weight Chart */}
      <div className="rounded-xl border bg-card p-5">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-semibold">Vazn (kg)</h2>
          <Button size="sm" variant="outline" onClick={() => setWeightModal(true)}>
            <Plus className="mr-1 h-3.5 w-3.5" /> Qo'shish
          </Button>
        </div>
        {weightData.length > 0 ? (
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={weightData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="date" fontSize={12} stroke="hsl(var(--muted-foreground))" />
              <YAxis domain={["dataMin - 1", "dataMax + 1"]} fontSize={12} stroke="hsl(var(--muted-foreground))" />
              <Tooltip />
              <Line type="monotone" dataKey="kg" stroke="hsl(var(--primary))" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="py-8 text-center text-sm text-muted-foreground">Ma'lumot yo'q</p>
        )}
      </div>

      {/* Weekly Calories */}
      <div className="rounded-xl border bg-card p-5">
        <h2 className="mb-4 font-semibold">Haftalik kaloriyalar (kcal)</h2>
        {macroData.length > 0 ? (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={macroData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="date" fontSize={12} stroke="hsl(var(--muted-foreground))" />
              <YAxis fontSize={12} stroke="hsl(var(--muted-foreground))" />
              <Tooltip />
              <Bar dataKey="calories" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
              {user?.daily_calorie_goal && (
                <ReferenceLine y={user.daily_calorie_goal} stroke="hsl(var(--destructive))" strokeDasharray="4 4" />
              )}
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="py-8 text-center text-sm text-muted-foreground">Ma'lumot yo'q</p>
        )}
      </div>

      {/* Weekly Water */}
      <div className="rounded-xl border bg-card p-5">
        <h2 className="mb-4 font-semibold">Haftalik suv (ml)</h2>
        {waterData.length > 0 ? (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={waterData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="date" fontSize={12} stroke="hsl(var(--muted-foreground))" />
              <YAxis fontSize={12} stroke="hsl(var(--muted-foreground))" />
              <Tooltip />
              <Bar dataKey="ml" fill="hsl(var(--water))" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="py-8 text-center text-sm text-muted-foreground">Ma'lumot yo'q</p>
        )}
      </div>

      {/* BMR/TDEE */}
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-xl border bg-card p-4 text-center">
          <Activity className="mx-auto mb-1 h-5 w-5 text-primary" />
          <p className="text-2xl font-bold">{Math.round(parseFloat(user?.bmr || "0"))}</p>
          <p className="text-xs text-muted-foreground">BMR (kcal)</p>
          <p className="mt-1 text-[10px] text-muted-foreground">Dam olishdagi kaloriya sarfi</p>
        </div>
        <div className="rounded-xl border bg-card p-4 text-center">
          <Flame className="mx-auto mb-1 h-5 w-5 text-carbs" />
          <p className="text-2xl font-bold">{Math.round(parseFloat(user?.tdee || "0"))}</p>
          <p className="text-xs text-muted-foreground">TDEE (kcal)</p>
          <p className="mt-1 text-[10px] text-muted-foreground">Kunlik umumiy kaloriya sarfi</p>
        </div>
      </div>

      {/* Weight Modal */}
      <Dialog open={weightModal} onOpenChange={setWeightModal}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Vazn qo'shish</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <Input type="date" value={newDate} onChange={(e) => setNewDate(e.target.value)} />
            <Input type="number" step="0.1" placeholder="Vazn (kg)" value={newWeight} onChange={(e) => setNewWeight(e.target.value)} />
            <Button className="w-full" onClick={addWeight}>Saqlash</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
