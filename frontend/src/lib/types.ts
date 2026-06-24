export interface DailyForecast {
  date: string;
  current_price: number;
  range_low: number;
  range_high: number;
  range_very_low: number;
  range_very_high: number;
  probabilities: {
    qalxma: number;
    enme: number;
    sabit: number;
  };
  mood: string;
  summary: string;
  summary_simple: string;
  note: string;
  for_user: string;
  analysis_basis?: {
    yearly_trend_score: number;
    news_score: number;
    technical_score: number;
    intraday_score: number;
    composite_score: number;
    articles_analyzed: number;
  };
  analysis_steps?: Array<{ title: string; text: string }>;
}

export interface AnalysisReport {
  steps: Array<{ title: string; text: string }>;
  yearly: Record<string, unknown>;
  news: Record<string, unknown>;
  intraday: Record<string, unknown>;
  composite_score: number;
}

export interface Probabilities {
  yüksəliş_ehtimalı: number;
  eniş_ehtimalı: number;
  neytral: number;
}

export interface PricePanel {
  symbol: string;
  name: string;
  price: number;
  daily_change: number;
  daily_change_pct: number;
  week_change_pct: number;
  week_trend: string;
  week_trend_explanation: string;
  volume: number;
  market_cap?: number;
  market_state?: string;
  updated_at: string;
  data_source?: string;
}

export interface Signal {
  signal: string;
  signal_key: string;
  confidence_pct: number;
  probabilities: Probabilities;
  risk_level: string;
  reason: string;
  price: number;
  stop_loss: number;
  take_profit: number;
  atr: number;
  atr_explanation: string;
  disclaimer: string;
}

export interface TechnicalAnalysis {
  price: number;
  rsi: { value: number; explanation: string };
  macd: { macd: number; signal: number; histogram: number; explanation: string };
  ema: { ema20: number; ema50: number; ema200: number; explanation: string };
  bollinger: { upper: number; middle: number; lower: number; explanation: string };
  volume: { current: number; average_20d: number; ratio: number; explanation: string };
  technical_bias_score: number;
}

export interface NewsItem {
  title: string;
  source: string;
  url: string;
  published_at: string;
  category: string;
  sentiment: string;
  impact_strength: number;
  summary: string;
}

export interface SentimentFactor {
  title: string;
  strength: number;
  category: string;
  explanation: string;
}

export interface Sentiment {
  mood: string;
  mood_explanation: string;
  probabilities: Probabilities;
  sentiment_score: number;
  bullish_factors: SentimentFactor[];
  bearish_factors: SentimentFactor[];
  risk_factors: SentimentFactor[];
  disclaimer: string;
}

export interface BacktestSignal {
  date: string;
  signal: string;
  entry_price: number;
  exit_price: number;
  pnl_pct: number;
  success: boolean;
  score: number;
}

export interface Backtest {
  period_days: number;
  total_signals: number;
  success_rate: number;
  loss_rate: number;
  avg_return_pct: number;
  buy_success_rate?: number;
  signals: BacktestSignal[];
  disclaimer: string;
}

export interface Risk {
  capital: number;
  risk_level: string;
  risk_score: number;
  risk_summary: string;
  recommended_investment_pct: number;
  recommended_investment_usd: number;
  max_loss_usd: number;
  max_loss_pct_of_capital: number;
  atr_pct: number;
  stop_loss: number;
  take_profit: number;
  shares_suggested: number;
  actual_investment: number;
  explanation: string;
  disclaimer: string;
}

export interface ChartPoint {
  date: string;
  timestamp?: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface DashboardData {
  price: PricePanel;
  signal: Signal;
  daily_forecast?: DailyForecast;
  technical: TechnicalAnalysis;
  sentiment: Sentiment;
  news: NewsItem[];
  backtest_30: Backtest;
  backtest_90: Backtest;
  risk: Risk;
  chart: ChartPoint[];
  chart_yearly: ChartPoint[];
  analysis_report?: AnalysisReport;
}
