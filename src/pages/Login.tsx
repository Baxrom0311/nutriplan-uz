import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { getApiErrorMessage } from "@/lib/apiError";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Leaf } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((s) => s.login);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    
    // Retry logic for cold start
    let attempts = 0;
    const maxAttempts = 2;
    
    while (attempts < maxAttempts) {
      try {
        await login(email, password);
        navigate("/dashboard");
        return;
      } catch (error: unknown) {
        attempts++;
        
        // Agar 500 xatosi va birinchi urinish bo'lsa, qayta urinish
        const errorMessage = getApiErrorMessage(error, "");
        const is500Error = errorMessage.includes("500") || errorMessage.includes("Network Error");
        
        if (is500Error && attempts < maxAttempts) {
          setError("Server uyg'onmoqda, qayta urinilmoqda...");
          await new Promise(resolve => setTimeout(resolve, 2000)); // 2 soniya kutish
          continue;
        }
        
        // Oxirgi urinish yoki boshqa xato
        setError(getApiErrorMessage(error, "Login xatoligi. Qayta urinib ko'ring."));
        break;
      }
    }
    
    setLoading(false);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-secondary/30 px-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="flex flex-col items-center gap-2">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary">
            <Leaf className="h-6 w-6 text-primary-foreground" />
          </div>
          <h1 className="text-2xl font-bold">NutriPlan UZ</h1>
          <p className="text-sm text-muted-foreground">Hisobingizga kiring</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border bg-card p-6 shadow-sm">
          {error && <p className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">{error}</p>}

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="email@example.com" />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Parol</Label>
            <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required placeholder="••••••••" />
          </div>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Kirish..." : "Kirish"}
          </Button>
        </form>

        <p className="text-center text-sm text-muted-foreground">
          Hisobingiz yo'qmi?{" "}
          <Link to="/register" className="font-medium text-primary hover:underline">
            Ro'yxatdan o'tish
          </Link>
        </p>
      </div>
    </div>
  );
}
