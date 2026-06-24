"use client";

import { GlassCard, Badge, formatUSD } from "./ui/GlassCard";
import type { Backtest } from "@/lib/types";

interface Props {
  backtest30: Backtest;
  backtest90: Backtest;
}

function Stats({ data, label }: { data: Backtest; label: string }) {
  return (
    <div className="bg-slate-900/40 rounded-xl p-4 border border-slate-700/30">
      <p className="text-sm text-cyan-400 font-medium mb-3">{label}</p>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div>
          <p className="text-xl font-bold text-emerald-400">{data.success_rate}%</p>
          <p className="text-xs text-slate-500">Uğurlu</p>
        </div>
        <div>
          <p className="text-xl font-bold text-red-400">{data.loss_rate}%</p>
          <p className="text-xs text-slate-500">Uğursuz</p>
        </div>
        <div>
          <p className={`text-xl font-bold ${data.avg_return_pct >= 0 ? "text-emerald-400" : "text-red-400"}`}>
            {data.avg_return_pct > 0 ? "+" : ""}{data.avg_return_pct}%
          </p>
          <p className="text-xs text-slate-500">Orta</p>
        </div>
      </div>
    </div>
  );
}

export function BacktestPanel({ backtest30, backtest90 }: Props) {
  return (
    <GlassCard title="Keçmişdə nə olub?">
      <p className="text-sm text-slate-400 mb-3 leading-relaxed">
        Əvvəlki günlərdə siqnallar nə qədər düz çıxıb — sadəcə məlumat üçündür.
      </p>
      <div className="space-y-3">
        <Stats data={backtest30} label="Son 30 gün" />
        <Stats data={backtest90} label="Son 3 ay" />
        <p className="text-xs text-amber-500/80 italic text-center">{backtest30.disclaimer}</p>
      </div>
    </GlassCard>
  );
}
