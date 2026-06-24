"use client";

import { useState } from "react";
import { GlassCard, Badge, formatUSD } from "./ui/GlassCard";
import type { Risk } from "@/lib/types";
import { API_URL } from "@/lib/api";

interface Props {
  initial: Risk;
}

export function RiskPanel({ initial }: Props) {
  const [capital, setCapital] = useState(initial.capital);
  const [risk, setRisk] = useState(initial);
  const [loading, setLoading] = useState(false);

  async function updateRisk(newCapital: number) {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/dashboard?capital=${newCapital}&refresh=true`);
      const data = await res.json();
      setRisk(data.risk);
    } catch {
      /* keep */
    } finally {
      setLoading(false);
    }
  }

  return (
    <GlassCard title="Nə qədər investisiya etməli?" glow="green">
      <div className="space-y-5">
        <div>
          <label className="text-base text-slate-300 block mb-2">
            Sənin pulun (USD): <span className="text-neon-green font-bold">{formatUSD(capital)}</span>
          </label>
          <input
            type="range"
            min={1000}
            max={100000}
            step={1000}
            value={capital}
            onChange={(e) => {
              const v = Number(e.target.value);
              setCapital(v);
              updateRisk(v);
            }}
            className="w-full h-3 accent-emerald-400 cursor-pointer"
          />
          <p className="text-xs text-slate-500 mt-1">Sürüşdür — öz pulunu yaz</p>
        </div>

        {loading ? (
          <p className="text-slate-400 animate-pulse">Hesablanır...</p>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-cyan-500/10 border border-cyan-500/20 rounded-xl p-4 text-center">
                <p className="text-sm text-cyan-400 mb-1">Tövsiyə olunan məbləğ</p>
                <p className="text-2xl font-bold text-cyan-300">{formatUSD(risk.recommended_investment_usd)}</p>
                <p className="text-xs text-slate-500 mt-1">Pulunun {risk.recommended_investment_pct}%</p>
              </div>
              <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-center">
                <p className="text-sm text-red-400 mb-1">Ən çox nə qədər itirə bilərsən</p>
                <p className="text-2xl font-bold text-red-300">{formatUSD(risk.max_loss_usd)}</p>
                <p className="text-xs text-slate-500 mt-1">Pulunun {risk.max_loss_pct_of_capital}%</p>
              </div>
            </div>

            <p className="text-base text-slate-300 leading-relaxed bg-slate-900/40 rounded-xl p-4">
              {risk.risk_level === "Yüksək"
                ? "⚠️ İndi bazar risklidir — az məbləğlə başla."
                : risk.risk_level === "Aşağı"
                  ? "✅ Bazar nisbətən sakitdir, amma yenə də ehtiyatlı ol."
                  : "ℹ️ Orta risk — çox da çox da az yatırma."}
            </p>
          </>
        )}
      </div>
    </GlassCard>
  );
}
