import { useState, useEffect } from "react";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Lightbulb, TrendingUp, AlertTriangle, Sparkles, RefreshCw } from "lucide-react";

interface InsightsData {
  context: {
    profile: {
      gender: string;
      height: number;
      current_weight: number;
      goal: string;
      activity_level: string;
      bmr: number;
      tdee: number;
    };
    targets: {
      calories: number;
      protein: number;
      carbs: number;
      fat: number;
    };
    last_7_days: {
      days_logged: number;
      total_days: number;
      avg_calories: number;
      avg_protein: number;
      avg_carbs: number;
      avg_fat: number;
      weight_change_kg: number;
    };
  };
  insights: {
    summary: string;
    recommendations: string[];
    warnings: string[];
    motivation: string;
  };
}

export default function InsightsPage() {
  const [data, setData] = useState<InsightsData | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchInsights = async () => {
    setLoading(true);
    try {
      const response = await api.get("/nutrition/insights/");
      setData(response.data);
    } catch (error) {
      console.error("Insights olishda xatolik:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="mx-auto max-w-4xl p-6">
        <Card className="p-8 text-center">
          <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-yellow-500" />
          <h2 className="text-xl font-semibold mb-2">Ma'lumot topilmadi</h2>
          <p className="text-muted-foreground mb-4">
            AI xulosalarini olish uchun profil va ovqat ma'lumotlarini kiriting
          </p>
          <Button onClick={fetchInsights}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Qayta urinish
          </Button>
        </Card>
      </div>
    );
  }

  const { context, insights } = data;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">AI Xulosalar</h1>
        <Button onClick={fetchInsights} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Yangilash
        </Button>
      </div>

      {/* Umumiy xulosa */}
      <Card className="p-6 bg-gradient-to-br from-primary/10 to-primary/5">
        <div className="flex items-start gap-3">
          <Sparkles className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
          <div>
            <h2 className="text-lg font-semibold mb-2">Umumiy holat</h2>
            <p className="text-muted-foreground leading-relaxed">{insights.summary}</p>
          </div>
        </div>
      </Card>

      {/* Statistika */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-4">
          <div className="text-sm text-muted-foreground mb-1">Jurnal yuritilgan</div>
          <div className="text-2xl font-bold">
            {context.last_7_days.days_logged}/{context.last_7_days.total_days}
          </div>
          <div className="text-xs text-muted-foreground">kunlar</div>
        </Card>

        <Card className="p-4">
          <div className="text-sm text-muted-foreground mb-1">O'rtacha kaloriya</div>
          <div className="text-2xl font-bold">{Math.round(context.last_7_days.avg_calories)}</div>
          <div className="text-xs text-muted-foreground">
            Maqsad: {context.targets.calories} kcal
          </div>
        </Card>

        <Card className="p-4">
          <div className="text-sm text-muted-foreground mb-1">Vazn o'zgarishi</div>
          <div className={`text-2xl font-bold ${
            context.last_7_days.weight_change_kg > 0 ? 'text-red-500' : 
            context.last_7_days.weight_change_kg < 0 ? 'text-green-500' : ''
          }`}>
            {context.last_7_days.weight_change_kg > 0 ? '+' : ''}
            {context.last_7_days.weight_change_kg} kg
          </div>
          <div className="text-xs text-muted-foreground">oxirgi 7 kun</div>
        </Card>
      </div>

      {/* Tavsiyalar */}
      {insights.recommendations && insights.recommendations.length > 0 && (
        <Card className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Lightbulb className="h-5 w-5 text-yellow-500" />
            <h2 className="text-lg font-semibold">Tavsiyalar</h2>
          </div>
          <ul className="space-y-3">
            {insights.recommendations.map((rec, index) => (
              <li key={index} className="flex items-start gap-3">
                <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-semibold text-primary">{index + 1}</span>
                </div>
                <p className="text-muted-foreground leading-relaxed">{rec}</p>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Ogohlantirishlar */}
      {insights.warnings && insights.warnings.length > 0 && (
        <Card className="p-6 border-yellow-500/50 bg-yellow-50 dark:bg-yellow-950/20">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="h-5 w-5 text-yellow-600 dark:text-yellow-500" />
            <h2 className="text-lg font-semibold">Diqqat!</h2>
          </div>
          <ul className="space-y-2">
            {insights.warnings.map((warning, index) => (
              <li key={index} className="text-yellow-800 dark:text-yellow-200">
                • {warning}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Motivatsiya */}
      {insights.motivation && (
        <Card className="p-6 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-950/20 dark:to-blue-950/20">
          <div className="flex items-center gap-3">
            <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
            <p className="text-lg font-medium text-green-900 dark:text-green-100">
              {insights.motivation}
            </p>
          </div>
        </Card>
      )}

      {/* Makronutrientlar */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Oxirgi 7 kun o'rtacha</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <div className="text-sm text-muted-foreground mb-1">Protein</div>
            <div className="text-xl font-bold">{Math.round(context.last_7_days.avg_protein)}g</div>
            <div className="text-xs text-muted-foreground">Maqsad: {context.targets.protein}g</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground mb-1">Uglevodlar</div>
            <div className="text-xl font-bold">{Math.round(context.last_7_days.avg_carbs)}g</div>
            <div className="text-xs text-muted-foreground">Maqsad: {context.targets.carbs}g</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground mb-1">Yog'</div>
            <div className="text-xl font-bold">{Math.round(context.last_7_days.avg_fat)}g</div>
            <div className="text-xs text-muted-foreground">Maqsad: {context.targets.fat}g</div>
          </div>
        </div>
      </Card>
    </div>
  );
}
