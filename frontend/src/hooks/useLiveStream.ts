"use client";

import { useEffect, useRef, useCallback } from "react";
import type { ChartPoint, PricePanel } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WS_URL = API_URL.replace(/^http/, "ws");

export interface LiveTick {
  quote: {
    price: number;
    daily_change: number;
    daily_change_pct: number;
    volume: number;
    market_state: string;
    is_market_active?: boolean;
    updated_at: string;
    data_source: string;
  };
  intraday: ChartPoint[];
  market_active: boolean;
  interval_sec: number;
}

interface UseLiveStreamOptions {
  onTick: (tick: LiveTick) => void;
  onStatus?: (connected: boolean, marketActive: boolean) => void;
}

export function useLiveStream({ onTick, onStatus }: UseLiveStreamOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const onTickRef = useRef(onTick);
  const onStatusRef = useRef(onStatus);

  onTickRef.current = onTick;
  onStatusRef.current = onStatus;

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(`${WS_URL}/api/ws/live`);
    wsRef.current = ws;

    ws.onopen = () => {
      onStatusRef.current?.(true, false);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as LiveTick;
        onTickRef.current(data);
        onStatusRef.current?.(true, data.market_active);
      } catch {
        /* ignore parse errors */
      }
    };

    ws.onclose = () => {
      onStatusRef.current?.(false, false);
      reconnectRef.current = setTimeout(connect, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      wsRef.current?.close();
    };
  }, [connect]);
}

export function mergePricePanel(prev: PricePanel, quote: LiveTick["quote"]): PricePanel {
  const marketOpen = quote.market_state === "REGULAR";
  return {
    ...prev,
    price: quote.price,
    daily_change: quote.daily_change,
    daily_change_pct: quote.daily_change_pct,
    volume: quote.volume,
    market_state: quote.market_state,
    updated_at: quote.updated_at,
    data_source: marketOpen ? "Yahoo Finance (canlı axın)" : "Yahoo Finance",
  };
}
