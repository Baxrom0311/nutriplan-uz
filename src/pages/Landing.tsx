import { Navigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Leaf, ArrowRight } from "lucide-react";

export default function LandingPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  if (accessToken) return <Navigate to="/dashboard" replace />;

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-secondary/30 px-4">
      <div className="flex flex-col items-center gap-6 text-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary">
          <Leaf className="h-8 w-8 text-primary-foreground" />
        </div>
        <div>
          <h1 className="text-4xl font-bold tracking-tight">NutriPlan UZ</h1>
          <p className="mt-2 text-lg text-muted-foreground">
            Sog'lom ovqatlanish — oddiy va qulay
          </p>
        </div>
        <div className="flex gap-3">
          <Button asChild size="lg">
            <Link to="/register">
              Boshlash <ArrowRight className="ml-1 h-4 w-4" />
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link to="/login">Kirish</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
