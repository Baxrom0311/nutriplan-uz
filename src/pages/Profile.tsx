import { useState, useEffect } from "react";
import { useAuthStore } from "@/stores/authStore";
import { useNavigate } from "react-router-dom";
import { ACTIVITY_LABELS, GOAL_LABELS, type UserProfile } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { LogOut, Calculator } from "lucide-react";

type ProfileFormState = Pick<
  UserProfile,
  "gender" | "birth_date" | "height_cm" | "weight_kg" | "activity_level" | "goal"
>;

const buildProfileForm = (user: UserProfile | null): ProfileFormState => ({
  gender: user?.gender || "male",
  birth_date: user?.birth_date || "",
  height_cm: user?.height_cm || "",
  weight_kg: user?.weight_kg || "",
  activity_level: user?.activity_level || "sedentary",
  goal: user?.goal || "maintain_weight",
});

export default function ProfilePage() {
  const { user, updateProfile, recalculate, logout, fetchProfile } = useAuthStore();
  const navigate = useNavigate();
  const [form, setForm] = useState<ProfileFormState>(() => buildProfileForm(user));
  const [saving, setSaving] = useState(false);
  const [calculating, setCalculating] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  useEffect(() => {
    if (user) {
      setForm(buildProfileForm(user));
    }
  }, [user]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateProfile(form);
      toast.success("Saqlandi!");
    } catch {
      toast.error("Xatolik");
    } finally {
      setSaving(false);
    }
  };

  const handleRecalculate = async () => {
    setCalculating(true);
    try {
      await recalculate();
      toast.success("Maqsadlar qayta hisoblandi!");
    } catch {
      toast.error("Xatolik");
    } finally {
      setCalculating(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-2xl font-bold">Profil</h1>

      <div className="space-y-4 rounded-xl border bg-card p-5">
        <div className="space-y-2">
          <Label>Jins</Label>
          <div className="flex gap-3">
            {(["male", "female"] as const).map((g) => (
              <button
                key={g}
                onClick={() => setForm((p) => ({ ...p, gender: g }))}
                className={`flex-1 rounded-lg border px-4 py-2.5 text-sm font-medium transition-colors ${
                  form.gender === g ? "border-primary bg-primary/10 text-primary" : "hover:bg-accent"
                }`}
              >
                {g === "male" ? "Erkak" : "Ayol"}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <Label>Tug'ilgan sana</Label>
          <Input type="date" value={form.birth_date} onChange={(e) => setForm((p) => ({ ...p, birth_date: e.target.value }))} />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label>Bo'y (cm)</Label>
            <Input type="number" value={form.height_cm} onChange={(e) => setForm((p) => ({ ...p, height_cm: e.target.value }))} />
          </div>
          <div className="space-y-2">
            <Label>Vazn (kg)</Label>
            <Input type="number" value={form.weight_kg} onChange={(e) => setForm((p) => ({ ...p, weight_kg: e.target.value }))} />
          </div>
        </div>

        <div className="space-y-2">
          <Label>Faollik darajasi</Label>
          <Select
            value={form.activity_level}
            onValueChange={(value: ProfileFormState["activity_level"]) =>
              setForm((prev) => ({ ...prev, activity_level: value }))
            }
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(ACTIVITY_LABELS).map(([k, v]) => (
                <SelectItem key={k} value={k}>{v}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Maqsad</Label>
          <Select
            value={form.goal}
            onValueChange={(value: ProfileFormState["goal"]) => setForm((prev) => ({ ...prev, goal: value }))}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(GOAL_LABELS).map(([k, v]) => (
                <SelectItem key={k} value={k}>{v}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Button className="w-full" onClick={handleSave} disabled={saving}>
          {saving ? "Saqlanmoqda..." : "Saqlash"}
        </Button>
      </div>

      {/* Goals display */}
      <div className="rounded-xl border bg-card p-5">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="font-semibold">Maqsadlar</h2>
          <Button size="sm" variant="outline" onClick={handleRecalculate} disabled={calculating}>
            <Calculator className="mr-1 h-3.5 w-3.5" />
            {calculating ? "..." : "Qayta hisoblash"}
          </Button>
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="rounded-lg bg-muted p-3">
            <p className="text-muted-foreground">Kunlik kaloriya</p>
            <p className="text-lg font-bold">{user?.daily_calorie_goal || "—"} kcal</p>
          </div>
          <div className="rounded-lg bg-muted p-3">
            <p className="text-muted-foreground">BMR</p>
            <p className="text-lg font-bold">{Math.round(parseFloat(user?.bmr || "0"))} kcal</p>
          </div>
          <div className="rounded-lg bg-muted p-3">
            <p className="text-muted-foreground">Protein</p>
            <p className="text-lg font-bold">{Math.round(parseFloat(user?.protein_goal_g || "0"))} g</p>
          </div>
          <div className="rounded-lg bg-muted p-3">
            <p className="text-muted-foreground">Uglevodlar</p>
            <p className="text-lg font-bold">{Math.round(parseFloat(user?.carbs_goal_g || "0"))} g</p>
          </div>
          <div className="rounded-lg bg-muted p-3">
            <p className="text-muted-foreground">Yog'</p>
            <p className="text-lg font-bold">{Math.round(parseFloat(user?.fat_goal_g || "0"))} g</p>
          </div>
          <div className="rounded-lg bg-muted p-3">
            <p className="text-muted-foreground">TDEE</p>
            <p className="text-lg font-bold">{Math.round(parseFloat(user?.tdee || "0"))} kcal</p>
          </div>
        </div>
      </div>

      {/* Logout */}
      <Button variant="outline" className="w-full text-destructive hover:bg-destructive/10" onClick={handleLogout}>
        <LogOut className="mr-2 h-4 w-4" />
        Chiqish
      </Button>
    </div>
  );
}
