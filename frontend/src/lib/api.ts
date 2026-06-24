import type { DashboardData, PricePanel } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface LiveData {
  quote: {
    price: number;
    daily_change: number;
    daily_change_pct: number;
    volume: number;
    market_state: string;
    updated_at: string;
    data_source: string;
  };
  intraday: Array<{
    date: string;
    timestamp: string;
    close: number;
    volume: number;
  }>;
}

export async function fetchDashboard(
  capital: number = 10000,
  refresh: boolean = false
): Promise<DashboardData> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 45000);
  const refreshParam = refresh ? "&refresh=true" : "";

  try {
    const res = await fetch(
      `${API_URL}/api/dashboard?capital=${capital}${refreshParam}&_t=${Date.now()}`,
      { cache: "no-store", signal: controller.signal }
    );
    if (!res.ok) throw new Error("Dashboard məlumatları alına bilmədi");
    return res.json();
  } finally {
    clearTimeout(timeout);
  }
}

export async function fetchLive(refresh: boolean = false): Promise<LiveData> {
  const res = await fetch(
    `${API_URL}/api/live?refresh=${refresh}&_t=${Date.now()}`,
    { cache: "no-store" }
  );
  if (!res.ok) throw new Error("Canlı məlumat alına bilmədi");
  return res.json();
}

export { API_URL };
