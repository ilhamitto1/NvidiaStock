"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { GlassCard, formatUSD } from "./ui/GlassCard";
import type { ChartPoint, PricePanel } from "@/lib/types";

interface Props {
  chart: ChartPoint[];
  price: PricePanel;
  mode: "live" | "yearly";
  onModeChange: (mode: "live" | "yearly") => void;
  marketActive?: boolean;
}

export function ChartPanel({ chart, price, mode, onModeChange, marketActive }: Props) {
  if (!chart.length) {
    return (
      <GlassCard title="Qiymət qrafiki" className="h-full" glow="blue">
        <p className="text-slate-400 text-base">Qrafik yüklənir...</p>
      </GlassCard>
    );
  }

  const minPrice = Math.min(...chart.map((c) => c.low)) * 0.999;
  const maxPrice = Math.max(...chart.map((c) => c.high)) * 1.001;
  const isLive = mode === "live";

  return (
    <GlassCard title="Qiymət qrafiki" className="h-full" glow="blue">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
        <div>
          <p className="text-2xl sm:text-3xl font-bold text-neon-blue">{formatUSD(price.price)}</p>
          <p className="text-base text-slate-400 mt-1">
            {isLive ? "Bu günün qrafiki" : "Son 1 ilin qrafiki"}
            {marketActive && isLive && (
              <span className="ml-2 text-emerald-400">● canlı</span>
            )}
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => onModeChange("live")}
            className={`flex-1 sm:flex-none text-sm px-4 py-3 rounded-xl border min-h-[44px] ${
              isLive
                ? "bg-cyan-500/20 border-cyan-500/50 text-cyan-200"
                : "border-slate-600 text-slate-400"
            }`}
          >
            Bu gün
          </button>
          <button
            onClick={() => onModeChange("yearly")}
            className={`flex-1 sm:flex-none text-sm px-4 py-3 rounded-xl border min-h-[44px] ${
              !isLive
                ? "bg-cyan-500/20 border-cyan-500/50 text-cyan-200"
                : "border-slate-600 text-slate-400"
            }`}
          >
            1 il
          </button>
        </div>
      </div>

      <div className="h-[280px] sm:h-[360px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chart} margin={{ top: 5, right: 5, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#00d4ff" stopOpacity={0.4} />
                <stop offset="100%" stopColor="#00d4ff" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,212,255,0.08)" />
            <XAxis
              dataKey="date"
              tick={{ fill: "#64748b", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              interval={isLive ? "preserveStartEnd" : Math.floor(chart.length / 8)}
            />
            <YAxis
              domain={[minPrice, maxPrice]}
              tick={{ fill: "#64748b", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) => `$${v.toFixed(0)}`}
              width={55}
            />
            <Tooltip
              contentStyle={{
                background: "rgba(15,23,42,0.95)",
                border: "1px solid rgba(0,212,255,0.2)",
                borderRadius: "8px",
                fontSize: "12px",
              }}
              formatter={(value) => [formatUSD(Number(value)), "Qiymət"]}
            />
            <Area
              type="monotone"
              dataKey="close"
              stroke="#00d4ff"
              strokeWidth={2}
              fill="url(#priceGradient)"
              isAnimationActive={isLive}
              animationDuration={300}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </GlassCard>
  );
}
