"use client";

import { GlassCard, Badge } from "./ui/GlassCard";
import type { NewsItem } from "@/lib/types";

interface Props {
  news: NewsItem[];
}

export function NewsPanel({ news }: Props) {
  return (
    <GlassCard title="Son xəbərlər">
      <p className="text-sm text-slate-400 mb-3">Hamısı Azərbaycan dilindədir.</p>
      <div className="space-y-3 max-h-[480px] overflow-y-auto pr-1">
        {news.map((item, i) => (
          <article
            key={i}
            className="bg-slate-900/40 rounded-xl p-4 border border-slate-700/30"
          >
            <p className="text-base text-slate-100 leading-snug font-medium">{item.title}</p>
            <p className="text-xs text-slate-500 mt-2">{item.source}</p>

            <div className="flex flex-wrap gap-2 mt-3">
              <Badge variant={item.sentiment === "müsbət" ? "positive" : item.sentiment === "mənfi" ? "negative" : "neutral"}>
                {item.sentiment === "müsbət" ? "👍 Yaxşı" : item.sentiment === "mənfi" ? "👎 Pis" : "➡️ Normal"}
              </Badge>
            </div>

            {item.summary && (
              <p className="text-sm text-slate-400 mt-2 leading-relaxed">{item.summary}</p>
            )}
          </article>
        ))}
      </div>
    </GlassCard>
  );
}
