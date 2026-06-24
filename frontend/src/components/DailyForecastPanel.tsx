"use client";

import { GlassCard, ProbabilityBar, formatUSD } from "./ui/GlassCard";
import type { DailyForecast } from "@/lib/types";

interface Props {
  data: DailyForecast;
}

export function DailyForecastPanel({ data }: Props) {
  const basis = data.analysis_basis;

  return (
    <div className="glass glow-green p-5 sm:p-6 rounded-2xl border-2 border-emerald-500/20">
      <div className="text-center mb-5">
        <p className="text-emerald-400 text-sm font-medium mb-1">👋 Salam, Famil Dosdiyev!</p>
        <h2 className="text-xl sm:text-2xl font-bold text-white leading-snug">
          Bu günün təxmini qiymət aralığı
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          {data.date} · Bütün qrafiklər və xəbərlər analiz edildikdən sonra
        </p>
      </div>

      <div className="bg-slate-900/60 rounded-xl p-4 sm:p-5 text-center mb-5">
        <p className="text-slate-400 text-sm mb-2">İndi NVDA qiyməti</p>
        <p className="text-4xl sm:text-5xl font-bold text-neon-green">{formatUSD(data.current_price)}</p>
        <p className="text-lg sm:text-xl text-cyan-300 mt-4 font-medium leading-relaxed">
          Bu gün təxminən{" "}
          <span className="text-white font-bold">{formatUSD(data.range_low)}</span>
          {" — "}
          <span className="text-white font-bold">{formatUSD(data.range_high)}</span>
          {" "}arasında ola bilər
        </p>
        <p className="text-slate-300 text-base mt-3 leading-relaxed">{data.summary_simple}</p>
      </div>

      {basis && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-5 text-center text-xs">
          <div className="bg-slate-800/50 rounded-lg p-2">
            <p className="text-slate-500">İllik qrafik</p>
            <p className="text-cyan-400 font-bold text-lg">{basis.yearly_trend_score}</p>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-2">
            <p className="text-slate-500">Xəbərlər ({basis.articles_analyzed})</p>
            <p className="text-cyan-400 font-bold text-lg">{basis.news_score}</p>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-2">
            <p className="text-slate-500">Texniki</p>
            <p className="text-cyan-400 font-bold text-lg">{basis.technical_score}</p>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-2">
            <p className="text-slate-500">Ümumi bal</p>
            <p className="text-emerald-400 font-bold text-lg">{basis.composite_score}</p>
          </div>
        </div>
      )}

      <div className="space-y-3 mb-4">
        <ProbabilityBar label="📈 Qalxa bilər" value={data.probabilities.qalxma} color="#00ff88" />
        <ProbabilityBar label="📉 Enə bilər" value={data.probabilities.enme} color="#f87171" />
        <ProbabilityBar label="➡️ Dəyişməyə bilər" value={data.probabilities.sabit} color="#94a3b8" />
      </div>

      <div className="grid grid-cols-2 gap-3 text-center text-sm mb-4">
        <div className="bg-red-500/10 rounded-lg p-3 border border-red-500/20">
          <p className="text-red-400 text-xs">Ən aşağı (təxmini)</p>
          <p className="text-lg font-bold text-red-300">{formatUSD(data.range_very_low)}</p>
        </div>
        <div className="bg-emerald-500/10 rounded-lg p-3 border border-emerald-500/20">
          <p className="text-emerald-400 text-xs">Ən yüksək (təxmini)</p>
          <p className="text-lg font-bold text-emerald-300">{formatUSD(data.range_very_high)}</p>
        </div>
      </div>

      {data.analysis_steps && data.analysis_steps.length > 0 && (
        <details className="mt-4 rounded-xl bg-slate-900/40 border border-slate-700/30">
          <summary className="p-4 cursor-pointer text-slate-300 text-sm font-medium">
            🔍 Analiz necə aparıldı? (bura bas)
          </summary>
          <div className="px-4 pb-4 space-y-3 border-t border-slate-700/30 pt-3">
            {data.analysis_steps.map((step, i) => (
              <div key={i}>
                <p className="text-cyan-400 text-sm font-medium">{step.title}</p>
                <p className="text-slate-400 text-sm leading-relaxed mt-1">{step.text}</p>
              </div>
            ))}
          </div>
        </details>
      )}

      <p className="text-xs text-amber-400/90 text-center mt-4 leading-relaxed">{data.note}</p>
    </div>
  );
}
