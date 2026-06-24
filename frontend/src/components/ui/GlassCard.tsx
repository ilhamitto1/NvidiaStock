import type { ReactNode } from "react";

interface GlassCardProps {
  title?: string;
  children: ReactNode;
  className?: string;
  glow?: "blue" | "green" | "none";
}

export function GlassCard({ title, children, className = "", glow = "blue" }: GlassCardProps) {
  const glowClass = glow === "green" ? "glow-green" : glow === "blue" ? "glow-blue" : "";
  return (
    <div className={`glass ${glowClass} p-4 sm:p-5 ${className}`}>
      {title && (
        <h3 className="text-base sm:text-lg font-semibold text-white mb-4">
          {title}
        </h3>
      )}
      {children}
    </div>
  );
}

export function Badge({
  children,
  variant = "neutral",
}: {
  children: ReactNode;
  variant?: "positive" | "negative" | "neutral" | "warning";
}) {
  const colors = {
    positive: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    negative: "bg-red-500/20 text-red-400 border-red-500/30",
    neutral: "bg-slate-500/20 text-slate-300 border-slate-500/30",
    warning: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  };
  return (
    <span className={`inline-flex px-2 py-0.5 text-xs font-medium rounded border ${colors[variant]}`}>
      {children}
    </span>
  );
}

export function ProbabilityBar({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm sm:text-base">
        <span className="text-slate-300">{label}</span>
        <span className="font-bold" style={{ color }}>
          {value}%
        </span>
      </div>
      <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${value}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

export function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-grid">
      <div className="w-12 h-12 border-2 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin" />
      <p className="mt-4 text-cyan-400 text-sm animate-pulse-glow">NVDA analiz edilir...</p>
      <p className="mt-2 text-slate-500 text-xs">Backend cavab vermirsə, bir neçə saniyə gözləyin</p>
    </div>
  );
}

export function formatUSD(value: number): string {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}
