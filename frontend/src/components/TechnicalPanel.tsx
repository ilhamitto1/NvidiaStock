"use client";

import { GlassCard, Badge } from "./ui/GlassCard";
import type { TechnicalAnalysis } from "@/lib/types";

interface Props {
  data: TechnicalAnalysis;
}

function SimpleRow({ icon, title, text, status }: { icon: string; title: string; text: string; status?: string }) {
  return (
    <div className="border-b border-slate-700/30 pb-4 last:border-0 last:pb-0">
      <p className="text-base font-medium text-white mb-1">
        {icon} {title}
      </p>
      {status && (
        <Badge variant={status === "yaxşı" ? "positive" : status === "pis" ? "negative" : "neutral"}>
          {status === "yaxşı" ? "Yaxşı görünür" : status === "pis" ? "Zəif görünür" : "Normal"}
        </Badge>
      )}
      <p className="text-sm text-slate-300 leading-relaxed">{text}</p>
    </div>
  );
}

export function TechnicalPanel({ data }: Props) {
  const rsiStatus = data.rsi.value >= 70 ? "pis" : data.rsi.value <= 30 ? "yaxşı" : "normal";
  const macdStatus = data.macd.histogram > 0 ? "yaxşı" : data.macd.histogram < 0 ? "pis" : "normal";

  return (
    <GlassCard title="Qısa texniki baxış">
      <p className="text-sm text-slate-400 mb-4 leading-relaxed">
        Burada sadə dillə deyirik — nə baş verir. Rəqəmlərə baxmağa ehtiyac yoxdur.
      </p>

      <div className="space-y-4">
        <SimpleRow
          icon="🌡️"
          title="Qiymət çox qalxıbmı?"
          text={data.rsi.explanation.replace(/RSI \d+\.?\d*/g, "").trim() || "Qiymət hələ normal həddədir."}
          status={rsiStatus}
        />
        <SimpleRow
          icon="📊"
          title="Alıcılar güclüdürmü?"
          text={data.macd.explanation}
          status={macdStatus}
        />
        <SimpleRow icon="📈" title="Ümumi trend" text={data.ema.explanation} />
        <SimpleRow icon="📰" title="Həcm — maraq varmı?" text={data.volume.explanation} />
      </div>
    </GlassCard>
  );
}
