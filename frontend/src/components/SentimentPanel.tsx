"use client";

import { GlassCard, Badge, ProbabilityBar } from "./ui/GlassCard";
import type { Sentiment } from "@/lib/types";

interface Props {
  data: Sentiment;
}

export function SentimentPanel({ data }: Props) {
  const moodEmoji = data.sentiment_score >= 55 ? "😊" : data.sentiment_score <= 45 ? "😟" : "😐";
  const moodText =
    data.sentiment_score >= 55
      ? "Xəbərlər yaxşıdır"
      : data.sentiment_score <= 45
        ? "Xəbərlər pisdir"
        : "Xəbərlər qarışıqdır";

  return (
    <GlassCard title="Xəbərlər nə deyir?" glow="green">
      <div className="space-y-4">
        <div className="text-center py-3">
          <p className="text-4xl">{moodEmoji}</p>
          <p className="text-lg font-semibold text-white mt-1">{moodText}</p>
          <p className="text-sm text-slate-400 mt-1">{data.mood_explanation}</p>
        </div>

        <div className="space-y-2">
          <ProbabilityBar label="Yaxşı xəbər şansı" value={data.probabilities.yüksəliş_ehtimalı} color="#00ff88" />
          <ProbabilityBar label="Pis xəbər şansı" value={data.probabilities.eniş_ehtimalı} color="#f87171" />
        </div>

        {data.bullish_factors.length > 0 && (
          <div>
            <p className="text-sm text-emerald-400 font-medium mb-2">👍 Yaxşı xəbərlər</p>
            {data.bullish_factors.slice(0, 3).map((f, i) => (
              <p key={i} className="text-sm text-slate-300 mb-2 leading-snug">• {f.title}</p>
            ))}
          </div>
        )}

        {data.bearish_factors.length > 0 && (
          <div>
            <p className="text-sm text-red-400 font-medium mb-2">👎 Pis xəbərlər</p>
            {data.bearish_factors.slice(0, 3).map((f, i) => (
              <p key={i} className="text-sm text-slate-300 mb-2 leading-snug">• {f.title}</p>
            ))}
          </div>
        )}
      </div>
    </GlassCard>
  );
}
