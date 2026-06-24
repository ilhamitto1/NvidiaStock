"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { fetchDashboard } from "@/lib/api";
import { useLiveStream, mergePricePanel } from "@/hooks/useLiveStream";
import type { DashboardData, PricePanel as PricePanelType, ChartPoint } from "@/lib/types";
import { LoadingSpinner } from "@/components/ui/GlassCard";
import { DailyForecastPanel } from "@/components/DailyForecastPanel";
import { PricePanel } from "@/components/PricePanel";
import { SignalPanel } from "@/components/SignalPanel";
import { TechnicalPanel } from "@/components/TechnicalPanel";
import { ChartPanel } from "@/components/ChartPanel";
import { SentimentPanel } from "@/components/SentimentPanel";
import { NewsPanel } from "@/components/NewsPanel";
import { BacktestPanel } from "@/components/BacktestPanel";
import { RiskPanel } from "@/components/RiskPanel";

type ChartMode = "live" | "yearly";

export function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [livePrice, setLivePrice] = useState<PricePanelType | null>(null);
  const [liveChart, setLiveChart] = useState<ChartPoint[]>([]);
  const [yearlyChart, setYearlyChart] = useState<ChartPoint[]>([]);
  const [chartMode, setChartMode] = useState<ChartMode>("live");
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [marketActive, setMarketActive] = useState(false);
  const [lastUpdate, setLastUpdate] = useState("");
  const capital = 10000;
  const mounted = useRef(true);
  const priceRef = useRef<PricePanelType | null>(null);

  const loadFull = useCallback(async (force = false) => {
    try {
      if (force) setRefreshing(true);
      const dashboard = await fetchDashboard(capital, force);
      if (!mounted.current) return;
      setData(dashboard);
      setLivePrice(dashboard.price);
      priceRef.current = dashboard.price;
      setLiveChart(dashboard.chart);
      setYearlyChart(dashboard.chart_yearly ?? []);
      setLastUpdate(new Date().toLocaleTimeString("az-AZ"));
      setError(null);
    } catch {
      if (!mounted.current) return;
      setError("Sayt bağlantısı kəsildi. Bir az gözlə və ya Yenilə düyməsinə bas.");
    } finally {
      if (mounted.current) setRefreshing(false);
    }
  }, [capital]);

  useLiveStream({
    onTick: (tick) => {
      if (!mounted.current) return;
      setLiveChart(tick.intraday);
      setMarketActive(tick.market_active);
      setLastUpdate(new Date().toLocaleTimeString("az-AZ"));
      const base = priceRef.current;
      if (base) {
        const updated = mergePricePanel(base, tick.quote);
        priceRef.current = updated;
        setLivePrice(updated);
      }
    },
    onStatus: (_, active) => setMarketActive(active),
  });

  useEffect(() => {
    mounted.current = true;
    loadFull(true);
    const t = setInterval(() => loadFull(true), 120000);
    return () => {
      mounted.current = false;
      clearInterval(t);
    };
  }, [loadFull]);

  if (error && !data) {
    return (
      <div className="min-h-screen bg-grid flex items-center justify-center p-6">
        <div className="glass p-8 max-w-md text-center rounded-2xl">
          <p className="text-red-400 text-xl mb-3">Bağlantı xətası</p>
          <p className="text-slate-400 mb-6">{error}</p>
          <button onClick={() => loadFull(true)} className="btn-primary w-full">
            Yenidən cəhd et
          </button>
        </div>
      </div>
    );
  }

  if (!data) return <LoadingSpinner />;

  const priceData = livePrice ?? data.price;
  const activeChart = chartMode === "yearly" ? yearlyChart : liveChart;

  return (
    <div className="min-h-screen bg-grid pb-8">
      {/* Başlıq — Famil Dosdiyev */}
      <header className="border-b border-cyan-500/10 bg-slate-950/90 backdrop-blur-md sticky top-0 z-50 safe-top">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <p className="text-emerald-400 text-sm font-medium">❤️ Famil Dosdiyev üçün xüsusi hazırlanıb</p>
              <h1 className="text-xl sm:text-2xl font-bold text-white mt-1">NVDA — NVIDIA səhmi</h1>
              <p className="text-sm text-slate-400">Sadə dillə, aydın şəkildə</p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-500">
                {marketActive ? "🟢 Bazar açıq" : "🔴 Bazar bağlı"}
                {lastUpdate && ` · ${lastUpdate}`}
              </span>
              <button
                onClick={() => loadFull(true)}
                disabled={refreshing}
                className="btn-primary text-sm px-4 py-2 disabled:opacity-50"
              >
                {refreshing ? "..." : "Yenilə"}
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 pt-4 space-y-4">
        {/* 1. Bu günün proqnozu — ən vacib */}
        {data.daily_forecast && <DailyForecastPanel data={data.daily_forecast} />}

        {/* 2. Qiymət + nə etməli */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <PricePanel data={priceData} />
          <SignalPanel data={data.signal} />
        </div>

        {/* 3. Qrafik — tam en */}
        <ChartPanel
          chart={activeChart}
          price={priceData}
          mode={chartMode}
          onModeChange={setChartMode}
          marketActive={marketActive}
        />

        {/* 4. Xəbərlər + sentiment */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <SentimentPanel data={data.sentiment} />
          <NewsPanel news={data.news} />
        </div>

        {/* 5. Pul / risk */}
        <RiskPanel initial={data.risk} />

        {/* 6. Əlavə məlumat — aşağıda */}
        <details className="glass rounded-xl overflow-hidden">
          <summary className="p-4 cursor-pointer text-slate-300 text-base font-medium select-none">
            📋 Əlavə texniki məlumat (istəsən aç)
          </summary>
          <div className="p-4 pt-0 space-y-4 border-t border-slate-700/30">
            <TechnicalPanel data={data.technical} />
            <BacktestPanel backtest30={data.backtest_30} backtest90={data.backtest_90} />
          </div>
        </details>
      </main>

      <footer className="max-w-6xl mx-auto px-4 mt-8 text-center text-sm text-slate-500 leading-relaxed">
        <p>❤️ Bu sayt Famil Dosdiyev üçün hazırlanıb.</p>
        <p className="mt-1 text-xs">Investisiya məsləhəti deyil — yalnız məlumat üçündür.</p>
      </footer>
    </div>
  );
}
