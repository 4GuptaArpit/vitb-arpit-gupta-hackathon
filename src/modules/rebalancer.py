"""
Module A: Tactical High-Frequency Stock Index Rebalancer.
Dynamically rebalances a 20-stock basket from the S&P 100 based on
real-time sentiment signals from the NLP Risk Engine.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.engine import RiskSignal

# S&P 100 20-Stock Mock Index Basket across diverse sectors
INDEX_BASKET = [
    {"ticker": "AAPL", "company": "Apple Inc.", "sector": "Information Technology", "base_weight": 0.075},
    {"ticker": "MSFT", "company": "Microsoft Corp.", "sector": "Information Technology", "base_weight": 0.075},
    {"ticker": "NVDA", "company": "NVIDIA Corp.", "sector": "Semiconductors", "base_weight": 0.070},
    {"ticker": "AMZN", "company": "Amazon.com Inc.", "sector": "Consumer Discretionary", "base_weight": 0.060},
    {"ticker": "GOOGL", "company": "Alphabet Inc.", "sector": "Communication Services", "base_weight": 0.055},
    {"ticker": "META", "company": "Meta Platforms Inc.", "sector": "Communication Services", "base_weight": 0.050},
    {"ticker": "TSLA", "company": "Tesla Inc.", "sector": "Consumer Discretionary", "base_weight": 0.045},
    {"ticker": "JPM", "company": "JPMorgan Chase & Co.", "sector": "Financials", "base_weight": 0.055},
    {"ticker": "V", "company": "Visa Inc.", "sector": "Financials", "base_weight": 0.045},
    {"ticker": "XOM", "company": "Exxon Mobil Corp.", "sector": "Energy", "base_weight": 0.050},
    {"ticker": "CVX", "company": "Chevron Corp.", "sector": "Energy", "base_weight": 0.040},
    {"ticker": "UNH", "company": "UnitedHealth Group", "sector": "Healthcare", "base_weight": 0.050},
    {"ticker": "JNJ", "company": "Johnson & Johnson", "sector": "Healthcare", "base_weight": 0.045},
    {"ticker": "PFE", "company": "Pfizer Inc.", "sector": "Healthcare", "base_weight": 0.035},
    {"ticker": "WMT", "company": "Walmart Inc.", "sector": "Consumer Staples", "base_weight": 0.045},
    {"ticker": "PG", "company": "Procter & Gamble Co.", "sector": "Consumer Staples", "base_weight": 0.045},
    {"ticker": "CAT", "company": "Caterpillar Inc.", "sector": "Industrials", "base_weight": 0.040},
    {"ticker": "BA", "company": "Boeing Co.", "sector": "Aerospace & Defense", "base_weight": 0.040},
    {"ticker": "HD", "company": "Home Depot Inc.", "sector": "Consumer Discretionary", "base_weight": 0.040},
    {"ticker": "DIS", "company": "Walt Disney Co.", "sector": "Entertainment", "base_weight": 0.040}
]


@dataclass
class RebalanceEvent:
    timestamp: str
    trigger_signal_id: str
    ticker_affected: str
    sentiment_score: float
    sentiment_label: str
    weight_before_pct: float
    weight_after_pct: float
    delta_pct: float
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TacticalIndexRebalancer:
    """
    Dynamically adjusts portfolio constituent weights based on NLP sentiment signals.
    Applies sensitivity scaling and institutional diversification constraints.
    """

    def __init__(
        self,
        sensitivity_alpha: float = 0.35,
        min_weight: float = 0.010,   # 1.0% floor
        max_weight: float = 0.180    # 18.0% ceiling to avoid single-stock blowout
    ):
        self.sensitivity_alpha = sensitivity_alpha
        self.min_weight = min_weight
        self.max_weight = max_weight

        # Initialize current weights from base weights
        self.basket = pd.DataFrame(INDEX_BASKET)
        self.base_weights: Dict[str, float] = {
            row["ticker"]: float(row["base_weight"]) for _, row in self.basket.iterrows()
        }
        self.current_weights: Dict[str, float] = self.base_weights.copy()
        self.rebalance_history: List[RebalanceEvent] = []

    def get_current_state(self) -> pd.DataFrame:
        """Returns the current index constituent table with weights and sectors."""
        df = self.basket.copy()
        df["current_weight"] = df["ticker"].map(self.current_weights)
        df["current_weight_pct"] = (df["current_weight"] * 100.0).round(2)
        df["base_weight_pct"] = (df["base_weight"] * 100.0).round(2)
        df["weight_drift_pct"] = (df["current_weight_pct"] - df["base_weight_pct"]).round(2)
        return df

    def reset(self) -> pd.DataFrame:
        """Reset constituent weights back to baseline S&P 100 benchmark."""
        self.current_weights = self.base_weights.copy()
        self.rebalance_history = []
        return self.get_current_state()

    def rebalance_from_signal(self, signal: RiskSignal) -> Optional[RebalanceEvent]:
        """
        Adjust weight of target stock using Sentiment Score (-1.0 to 1.0).
        Positive sentiment -> weight increases.
        Negative sentiment -> weight decreases.
        """
        ticker = signal.ticker.upper()
        if ticker not in self.current_weights:
            return None

        old_weight = self.current_weights[ticker]

        # Multiplicative sentiment adjustment: w_new = w_old * (1 + alpha * sentiment)
        adjustment_factor = 1.0 + (self.sensitivity_alpha * signal.sentiment_score)
        tentative_weight = old_weight * adjustment_factor

        # Update and re-normalize the basket
        raw_weights = self.current_weights.copy()
        raw_weights[ticker] = tentative_weight

        normalized_weights = self._normalize_and_clamp(raw_weights)
        new_weight = normalized_weights[ticker]
        self.current_weights = normalized_weights

        delta = (new_weight - old_weight) * 100.0

        event = RebalanceEvent(
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            trigger_signal_id=signal.id,
            ticker_affected=ticker,
            sentiment_score=signal.sentiment_score,
            sentiment_label=signal.sentiment_label,
            weight_before_pct=round(old_weight * 100.0, 2),
            weight_after_pct=round(new_weight * 100.0, 2),
            delta_pct=round(delta, 2),
            summary=f"{signal.sentiment_label} signal ({signal.sentiment_score:+.2f}) -> {delta:+.2f}% delta"
        )
        self.rebalance_history.append(event)
        return event

    def rebalance_batch(self, signals: List[RiskSignal]) -> List[RebalanceEvent]:
        """Process a stream of signals and dynamically rebalance sequentially."""
        events: List[RebalanceEvent] = []
        for sig in signals:
            ev = self.rebalance_from_signal(sig)
            if ev:
                events.append(ev)
        return events

    def _normalize_and_clamp(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Enforces [min_weight, max_weight] boundaries and sums to 1.0."""
        # Step 1: Clamp within boundaries
        clamped = {
            t: max(self.min_weight, min(self.max_weight, w))
            for t, w in weights.items()
        }

        # Step 2: Normalize so sum equals exactly 1.0
        total = sum(clamped.values())
        if total <= 0:
            return {t: 1.0 / len(weights) for t in weights}

        normalized = {t: round(w / total, 6) for t, w in clamped.items()}

        # Minor residual correction to guarantee exact 1.0 sum
        diff = 1.0 - sum(normalized.values())
        first_key = next(iter(normalized))
        normalized[first_key] = round(normalized[first_key] + diff, 6)

        return normalized

    def backtest_vs_benchmark(self, signals: List[RiskSignal]) -> Dict[str, Any]:
        """Calculates quantitative alpha, Sharpe ratio, and drawdown vs static benchmark."""
        strat_returns = []
        bench_returns = []
        timestamps = []
        temp_weights = self.base_weights.copy()

        for sig in signals:
            timestamps.append(sig.timestamp[:19] if sig.timestamp else "N/A")
            # Conditioned asset return = sentiment * (impact / 10) * 0.025
            asset_ret = sig.sentiment_score * (sig.impact_score / 10.0) * 0.025
            bench_ret = asset_ret * self.base_weights.get(sig.ticker, 0.05)
            bench_returns.append(bench_ret)

            # Strategy dynamic weight allocation
            adj = 1.0 + (self.sensitivity_alpha * sig.sentiment_score)
            tentative = temp_weights.get(sig.ticker, 0.05) * adj
            raw = temp_weights.copy()
            raw[sig.ticker] = tentative
            temp_weights = self._normalize_and_clamp(raw)

            strat_ret = asset_ret * temp_weights.get(sig.ticker, 0.05)
            strat_returns.append(strat_ret)

        strat_cum = np.cumsum(strat_returns) if strat_returns else np.array([0.0])
        bench_cum = np.cumsum(bench_returns) if bench_returns else np.array([0.0])

        total_strat = float(strat_cum[-1]) if len(strat_cum) else 0.0
        total_bench = float(bench_cum[-1]) if len(bench_cum) else 0.0
        alpha_bps = float((total_strat - total_bench) * 10000.0)

        vol_s = float(np.std(strat_returns) * np.sqrt(252)) if len(strat_returns) > 1 and np.std(strat_returns) > 0 else 0.01
        vol_b = float(np.std(bench_returns) * np.sqrt(252)) if len(bench_returns) > 1 and np.std(bench_returns) > 0 else 0.01
        n = max(len(strat_returns), 1)
        sharpe_strat = float((total_strat * 252 / n - 0.045) / vol_s)
        sharpe_bench = float((total_bench * 252 / n - 0.045) / vol_b)

        peak_s = np.maximum.accumulate(strat_cum)
        peak_b = np.maximum.accumulate(bench_cum)
        mdd_s = float(np.min(strat_cum - peak_s)) if len(strat_cum) else 0.0
        mdd_b = float(np.min(bench_cum - peak_b)) if len(bench_cum) else 0.0

        return {
            "strategy_cumulative_return_pct": round(total_strat * 100.0, 3),
            "benchmark_cumulative_return_pct": round(total_bench * 100.0, 3),
            "alpha_bps": round(alpha_bps, 1),
            "alpha_percentage": round((total_strat - total_bench) * 100.0, 3),
            "strategy_sharpe": round(sharpe_strat, 2),
            "benchmark_sharpe": round(sharpe_bench, 2),
            "strategy_max_drawdown_pct": round(mdd_s * 100.0, 3),
            "benchmark_max_drawdown_pct": round(mdd_b * 100.0, 3),
            "time_series": [
                {"timestamp": t, "strategy_cum_pct": round(float(s) * 100.0, 3), "benchmark_cum_pct": round(float(b) * 100.0, 3)}
                for t, s, b in zip(timestamps, strat_cum, bench_cum)
            ]
        }

