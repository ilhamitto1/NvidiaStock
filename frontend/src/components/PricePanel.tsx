"use client";

import { GlassCard, Badge, formatUSD, formatNumber } from "./ui/GlassCard";
import type { PricePanel as PricePanelType } from "@/lib/types";

interface Props {
  data: PricePanelType;
}

export function PricePanel({ data }: Props) {
  const isPositive = data.daily_change >= 0;

  return (
    <GlassCard title="NVDA — indi neçəyədir?" glow="green">
      <div className="space-y-4">
        <div>
          <p className="text-sm text-slate-400">NVIDIA səhmi</p>
          <p className="text-4xl sm:text-5xl font-bold text-neon-green mt-1">{formatUSD(data.price)}</p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={isPositive ? "positive" : "negative"}>
            {isPositive ? "📈 Bu gün qalxıb" : "📉 Bu gün enib"}{" "}
            {isPositive ? "+" : ""}{data.daily_change_pct.toFixed(2)}%
          </Badge>
          <span className="text-base text-slate-300">
            ({isPositive ? "+" : ""}{formatUSD(data.daily_change)})
          </span>
        </div>

        <div className="pt-3 border-t border-slate-700/50 space-y-2">
          <div className="flex justify-between items-center text-base">
            <span className="text-slate-400">Son həftə</span>
            <Badge variant={data.week_trend === "Yüksəliş" ? "positive" : data.week_trend === "Eniş" ? "negative" : "neutral"}>
              {data.week_trend === "Yüksəliş" ? "📈 Qalxıb" : data.week_trend === "Eniş" ? "📉 Enib" : "➡️ Sabit"}
              {" "}({data.week_change_pct > 0 ? "+" : ""}{data.week_change_pct.toFixed(1)}%)
            </Badge>
          </div>
          <p className="text-sm text-slate-400 leading-relaxed">{data.week_trend_explanation}</p>
          {data.updated_at && (
            <p className="text-xs text-slate-500">
              Yeniləndi: {new Date(data.updated_at).toLocaleTimeString("az-AZ")}
            </p>
          )}
        </div>
      </div>
    </GlassCard>
  );
}
