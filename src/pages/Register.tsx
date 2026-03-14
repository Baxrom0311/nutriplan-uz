import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Leaf } from "lucide-react";

export default function RegisterPage() {
  const [form, setForm] = useState({ username: "", email: "", password: "", password2: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const register = useAuthStore((s) => s.register);
  const navigate = useNavigate();

  const update = (k: string, v: string) => setForm((p) => ({ ...p, [k]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (form.password !== form.password2) {
      setError("Parollar mos kelmadi");
      return;
    }
    setLoading(true);
    try {
      await register(form);
      navigate("/login");
    } catch (err: any) {
      const d = err.response?.data;
      const msg = d ? Object.values(d).flat().join(" ") : "Ro'yxatdan o'tishda xatolik";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-secondary/30 px-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="flex flex-col items-center gap-2">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary">
            <Leaf className="h-6 w-6 text-primary-foreground" />
          </div>
          <h1 className="text-2xl font-bold">NutriPlan UZ</h1>
          <p className="text-sm text-muted-foreground">Yangi hisob yarating</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border bg-card p-6 shadow-sm">
          {error && <p className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">{error}</p>}

          <div className="space-y-2">
            <Label>Foydalanuvchi nomi</Label>
            <Input value={form.username} onChange={(e) => update("username", e.target.value)} required placeholder="username" />
          </div>
          <div className="space-y-2">
            <Label>Email</Label>
            <Input type="email" value={form.email} onChange={(e) => update("email", e.target.value)} required placeholder="email@example.com" />
          </div>
          <div className="space-y-2">
            <Label>Parol</Label>
            <Input type="password" value={form.password} onChange={(e) => update("password", e.target.value)} required placeholder="••••••••" />
          </div>
          <div className="space-y-2">
            <Label>Parolni tasdiqlang</Label>
            <Input type="password" value={form.password2} onChange={(e) => update("password2", e.target.value)} required placeholder="••••••••" />
          </div>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Yaratilmoqda..." : "Ro'yxatdan o'tish"}
          </Button>
        </form>

        <p className="text-center text-sm text-muted-foreground">
          Hisobingiz bormi?{" "}
          <Link to="/login" className="font-medium text-primary hover:underline">
            Kirish
          </Link>
        </p>
      </div>
    </div>
  );
}
