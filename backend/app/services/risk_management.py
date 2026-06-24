from typing import Any

from app.services.market_data import get_ohlcv_dataframe
from app.services.signal_engine import generate_signal
import ta


async def calculate_risk(capital: float = 10000) -> dict[str, Any]:
    signal = await generate_signal()
    df = get_ohlcv_dataframe(90)
    atr = ta.volatility.AverageTrueRange(
        df["High"], df["Low"], df["Close"], window=14
    ).average_true_range().iloc[-1]
    price = signal["price"]
    atr_pct = (atr / price) * 100

    risk_pct_map = {"Aşağı": 1.0, "Orta": 2.0, "Yüksək": 3.0}
    risk_pct = risk_pct_map.get(signal["risk_level"], 2.0)

    recommended_investment = round(capital * (risk_pct / 100) * 10, 2)
    recommended_investment = min(recommended_investment, capital * 0.25)
    max_loss = round(recommended_investment * (atr_pct / 100) * 2, 2)

    stop_distance = price - signal["stop_loss"]
    shares = int(recommended_investment / price) if price else 0
    actual_investment = round(shares * price, 2)
    max_loss_at_stop = round(shares * stop_distance, 2) if shares else 0

    risk_score = min(100, round(atr_pct * 15 + (100 - signal["confidence_pct"]) * 0.3, 1))

    if risk_score >= 70:
        risk_summary = "Yüksək volatillik — kiçik investisiya ölçüsü tövsiyə olunur."
    elif risk_score >= 40:
        risk_summary = "Orta səviyyəli risk — balanslaşdırılmış yanaşma məqsədəuyğundur."
    else:
        risk_summary = "Aşağı risk — bazar nisbətən sabitdir, amma ehtiyatlı olun."

    return {
        "capital": capital,
        "risk_level": signal["risk_level"],
        "risk_score": risk_score,
        "risk_summary": risk_summary,
        "recommended_investment_pct": round(recommended_investment / capital * 100, 1),
        "recommended_investment_usd": round(recommended_investment, 2),
        "max_loss_usd": max_loss_at_stop or max_loss,
        "max_loss_pct_of_capital": round((max_loss_at_stop or max_loss) / capital * 100, 2),
        "atr_pct": round(atr_pct, 2),
        "stop_loss": signal["stop_loss"],
        "take_profit": signal["take_profit"],
        "shares_suggested": shares,
        "actual_investment": actual_investment,
        "explanation": (
            f"${capital:,.0f} kapitalınız varsa, tövsiyə olunan investisiya "
            f"${recommended_investment:,.0f} ({recommended_investment/capital*100:.1f}%) həcmindədir. "
            f"Stop loss səviyyəsində maksimum itki təxminən ${max_loss_at_stop or max_loss:,.0f} ola bilər."
        ),
        "disclaimer": "Bu risk hesablaması ehtimal əsaslıdır, maliyyə məsləhəti deyil.",
    }
