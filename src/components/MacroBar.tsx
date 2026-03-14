interface MacroBarProps {
  label: string;
  consumed: number;
  goal: number;
  color: string;
  unit?: string;
}

export default function MacroBar({ label, consumed, goal, color, unit = "g" }: MacroBarProps) {
  const pct = goal > 0 ? Math.min((consumed / goal) * 100, 100) : 0;

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium">{label}</span>
        <span className="text-muted-foreground">
          {consumed} / {goal} {unit}
        </span>
      </div>
      <div className="h-2.5 overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}
