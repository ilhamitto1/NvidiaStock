"use client";

import { GlassCard, Badge, ProbabilityBar, formatUSD } from "./ui/GlassCard";
import type { Signal } from "@/lib/types";

interface Props {
  data: Signal;
}

const SIGNAL_SIMPLE: Record<string, { label: string; emoji: string; explain: string }> = {
  "ÇOX GÜCLÜ AL": {
    label: "Yaxşı vaxtdır — almaq olar",
    emoji: "✅",
    explain: "Göstəricilər deyir ki, indi almaq üçün yaxşı şans var.",
  },
  AL: {
    label: "Almaq olar",
    emoji: "👍",
    explain: "Ümumilikdə vəziyyət yaxşıdır, amma ehtiyatlı olun.",
  },
  GÖZLƏ: {
    label: "Gözlə — tələsmə",
    emoji: "⏳",
    explain: "Hələ aydın deyil. Bir neçə gün gözləmək daha yaxşıdır.",
  },
  SAT: {
    label: "Satmaq düşünülə bilər",
    emoji: "⚠️",
    explain: "Qiymət zəifləyə bilər. Əgər səhmin varsa, satmağı düşün.",
  },
  "ÇOX GÜCLÜ SAT": {
    label: "Diqqət — satmaq vaxtı ola bilər",
    emoji: "🔴",
    explain: "Göstəricilər zəifdir. Sahib olduğun səhmləri satmağı düşün.",
  },
};

const RISK_SIMPLE: Record<string, string> = {
  Aşağı: "Az risk",
  Orta: "Orta risk",
  Yüksək: "Yüksək risk",
};

export function SignalPanel({ data }: Props) {
  const simple = SIGNAL_SIMPLE[data.signal] ?? {
    label: data.signal,
    emoji: "ℹ️",
    explain: data.reason,
  };

  return (
    <GlassCard title="Bu gün nə etməli?" glow="green">
      <div className="space-y-4">
        <div className="text-center py-4 rounded-xl bg-slate-900/50 border border-slate-700/40">
          <p className="text-4xl mb-2">{simple.emoji}</p>
          <p className="text-xl sm:text-2xl font-bold text-white leading-snug">{simple.label}</p>
          <p className="text-sm text-slate-400 mt-2 leading-relaxed px-2">{simple.explain}</p>
        </div>

        <div className="space-y-2">
          <ProbabilityBar label="Qalxma şansı" value={data.probabilities.yüksəliş_ehtimalı} color="#00ff88" />
          <ProbabilityBar label="Enmə şansı" value={data.probabilities.eniş_ehtimalı} color="#f87171" />
          <ProbabilityBar label="Dəyişməmə şansı" value={data.probabilities.neytral} color="#94a3b8" />
        </div>

        <div className="flex items-center justify-between text-base">
          <span className="text-slate-400">Risk</span>
          <Badge variant={data.risk_level === "Yüksək" ? "negative" : data.risk_level === "Aşağı" ? "positive" : "warning"}>
            {RISK_SIMPLE[data.risk_level] ?? data.risk_level}
          </Badge>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-3">
            <p className="text-red-400 text-xs mb-1">Əgər düşsə — dayan</p>
            <p className="font-bold text-red-300 text-lg">{formatUSD(data.stop_loss)}</p>
            <p className="text-xs text-slate-500 mt-1">Bu qiymətə düşsə, itki azalır</p>
          </div>
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-3">
            <p className="text-emerald-400 text-xs mb-1">Əgər qalxsa — sat</p>
            <p className="font-bold text-emerald-300 text-lg">{formatUSD(data.take_profit)}</p>
            <p className="text-xs text-slate-500 mt-1">Bu qiymətə çatsa, qazanc götür</p>
          </div>
        </div>

        <p className="text-xs text-amber-500/80 text-center">{data.disclaimer}</p>
      </div>
    </GlassCard>
  );
}
