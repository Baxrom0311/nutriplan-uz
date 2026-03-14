interface CalorieRingProps {
  consumed: number;
  goal: number;
  size?: number;
}

export default function CalorieRing({ consumed, goal, size = 200 }: CalorieRingProps) {
  const strokeWidth = 14;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = goal > 0 ? Math.min(consumed / goal, 1) : 0;
  const offset = circumference * (1 - progress);
  const remaining = goal - consumed;
  const isOver = remaining < 0;

  return (
    <div className="relative flex flex-col items-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="hsl(var(--muted))"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={isOver ? "hsl(var(--destructive))" : "hsl(var(--primary))"}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-700 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold">{consumed}</span>
        <span className="text-xs text-muted-foreground">/ {goal} kcal</span>
      </div>
      <p className={`mt-2 text-sm font-medium ${isOver ? "text-destructive" : "text-muted-foreground"}`}>
        {isOver ? `${Math.abs(remaining)} kcal ortiqcha` : `${remaining} kcal qoldi`}
      </p>
    </div>
  );
}
