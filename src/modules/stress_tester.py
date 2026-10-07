"""
Module B: Strategic Portfolio Stress-Testing Tool for Wholesale Banking Assets.
Simulates multi-factor macroeconomic and credit shocks on loans, bonds, and CDS
driven by NLP Risk Engine event classifications and impact severity scores.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

# Multi-factor shock matrix calibrated for wholesale banking stress testing
SHOCK_MATRIX: Dict[str, Dict[str, float]] = {
    "Credit Event": {
        "spread_widening_bps": 350.0,
        "pd_multiplier": 2.20,
        "rate_shift_pct": 0.00,
        "equity_haircut_pct": 0.12,
        "recovery_drop_pct": 0.15
    },
    "Geopolitical": {
        "spread_widening_bps": 280.0,
        "pd_multiplier": 1.75,
        "rate_shift_pct": 0.40,
        "equity_haircut_pct": 0.15,
        "recovery_drop_pct": 0.10
    },
    "Macroeconomic": {
        "spread_widening_bps": 200.0,
        "pd_multiplier": 1.50,
        "rate_shift_pct": 0.75,
        "equity_haircut_pct": 0.08,
        "recovery_drop_pct": 0.05
    },
    "Regulatory": {
        "spread_widening_bps": 120.0,
        "pd_multiplier": 1.25,
        "rate_shift_pct": 0.00,
        "equity_haircut_pct": 0.06,
        "recovery_drop_pct": 0.05
    },
    "Merger/Acquisition": {
        "spread_widening_bps": 80.0,
        "pd_multiplier": 1.10,
        "rate_shift_pct": 0.00,
        "equity_haircut_pct": 0.03,
        "recovery_drop_pct": 0.00
    },
    "Product Launch": {
        "spread_widening_bps": -40.0,     # Spread tightening / favorable
        "pd_multiplier": 0.90,
        "rate_shift_pct": 0.00,
        "equity_haircut_pct": -0.04,
        "recovery_drop_pct": 0.00
    }
}

# Landmark Historical Crisis Scenarios Playbook
HISTORICAL_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "2008 Lehman Liquidity Crunch": {
        "event_type": "Credit Event",
        "impact_score": 10,
        "target_sector": "Financial Services",
        "narrative": "Global liquidity freeze, subprime debt write-downs, systemic counterparty contagion."
    },
    "2020 COVID Market Dislocation": {
        "event_type": "Macroeconomic",
        "impact_score": 9,
        "target_sector": "None",
        "narrative": "Simultaneous supply/demand shock, emergency interest rate cuts, corporate cash drawdowns."
    },
    "2022 Geopolitical Energy & Shipping Crisis": {
        "event_type": "Geopolitical",
        "impact_score": 8,
        "target_sector": "Energy",
        "narrative": "Strait shipping rerouting, crude oil spike, maritime insurance surge and sanctions."
    },
    "2024 Tech Regulatory & Antitrust Sweep": {
        "event_type": "Regulatory",
        "impact_score": 7,
        "target_sector": "Semiconductors",
        "narrative": "EU Digital Markets Act enforcement, strict in-app fee crackdowns, cross-border export limits."
    }
}


@dataclass
class StressTestResult:
    event_type: str
    impact_score: int
    baseline_value_usd: float
    stressed_value_usd: float
    total_pnl_usd: float
    pnl_percentage: float
    baseline_expected_loss_usd: float
    stressed_expected_loss_usd: float
    el_increase_usd: float
    var_99_baseline_usd: float
    var_99_stressed_usd: float
    asset_breakdown: List[Dict[str, Any]]
    stressed_positions_df: Optional[pd.DataFrame] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "impact_score": self.impact_score,
            "baseline_value_usd": round(self.baseline_value_usd, 2),
            "stressed_value_usd": round(self.stressed_value_usd, 2),
            "total_pnl_usd": round(self.total_pnl_usd, 2),
            "pnl_percentage": round(self.pnl_percentage, 2),
            "baseline_expected_loss_usd": round(self.baseline_expected_loss_usd, 2),
            "stressed_expected_loss_usd": round(self.stressed_expected_loss_usd, 2),
            "el_increase_usd": round(self.el_increase_usd, 2),
            "var_99_baseline_usd": round(self.var_99_baseline_usd, 2),
            "var_99_stressed_usd": round(self.var_99_stressed_usd, 2),
            "asset_breakdown": self.asset_breakdown
        }


class StressTester:
    """Simulates strategic portfolio stress tests on wholesale banking portfolios."""

    def __init__(self, portfolio_path: Optional[str] = None):
        self.portfolio_path = Path(portfolio_path) if portfolio_path else Path("data/wholesale_portfolio.csv")
        self.portfolio_df = self._load_portfolio()

    def _load_portfolio(self) -> pd.DataFrame:
        """Loads and prepares the wholesale portfolio dataset."""
        if not self.portfolio_path.exists():
            raise FileNotFoundError(f"Portfolio file not found: {self.portfolio_path}")
        df = pd.read_csv(self.portfolio_path)
        return df

    def run_stress_test(
        self,
        event_type: str,
        impact_score: int,
        target_sector: Optional[str] = None
    ) -> StressTestResult:
        """
        Executes stress simulation scaling multi-factor shocks by impact severity (1-10).
        """
        severity_ratio = max(0.1, min(1.0, impact_score / 10.0))
        shocks = SHOCK_MATRIX.get(event_type, SHOCK_MATRIX["Macroeconomic"])

        scaled_spread_shift = (shocks["spread_widening_bps"] / 10000.0) * severity_ratio
        scaled_pd_mult = 1.0 + ((shocks["pd_multiplier"] - 1.0) * severity_ratio)
        scaled_rate_shift = (shocks["rate_shift_pct"] / 100.0) * severity_ratio

        df = self.portfolio_df.copy()
        stressed_mv_list = []
        baseline_el_list = []
        stressed_el_list = []

        for _, row in df.iterrows():
            mv = float(row["current_mv_usd"])
            tenor = float(row["tenor_years"])
            pd_base = float(row["pd_baseline_pct"]) / 100.0
            lgd_base = float(row["lgd_pct"]) / 100.0
            notional = float(row["notional_usd"])
            asset_type = str(row["asset_type"])
            sector = str(row["sector"])

            # If sector targeted, amplify shock for that sector
            multiplier = 1.4 if (target_sector and sector.lower() == target_sector.lower()) else 1.0

            # 1. Modified Duration MTM impact approximation
            eff_duration = max(1.0, tenor * 0.85)
            spread_impact_pct = -(eff_duration * scaled_spread_shift * multiplier)
            rate_impact_pct = -(eff_duration * scaled_rate_shift * multiplier)

            if asset_type == "Credit Default Swap":
                # CDS protection sold experiences negative MTM as spreads widen
                net_price_shock = -(eff_duration * scaled_spread_shift * 1.5 * multiplier)
            else:
                net_price_shock = spread_impact_pct + rate_impact_pct

            # Limit extreme single position drops to realistic wholesale ranges
            net_price_shock = max(-0.45, min(0.15, net_price_shock))
            stressed_mv = mv * (1.0 + net_price_shock)

            # 2. Credit Risk - Expected Loss: EL = EAD * PD * LGD
            base_el = notional * pd_base * lgd_base
            stressed_pd = min(0.60, pd_base * (scaled_pd_mult ** multiplier))
            stressed_lgd = min(0.90, lgd_base * (1.0 + shocks["recovery_drop_pct"] * severity_ratio))
            stressed_el = notional * stressed_pd * stressed_lgd

            stressed_mv_list.append(stressed_mv)
            baseline_el_list.append(base_el)
            stressed_el_list.append(stressed_el)

        df["stressed_mv_usd"] = stressed_mv_list
        df["pnl_usd"] = df["stressed_mv_usd"] - df["current_mv_usd"]
        df["pnl_pct"] = (df["pnl_usd"] / df["current_mv_usd"]) * 100.0
        df["baseline_el_usd"] = baseline_el_list
        df["stressed_el_usd"] = stressed_el_list

        base_val = float(df["current_mv_usd"].sum())
        stressed_val = float(df["stressed_mv_usd"].sum())
        total_pnl = stressed_val - base_val
        pnl_pct = (total_pnl / base_val) * 100.0

        base_el_sum = float(df["baseline_el_usd"].sum())
        stressed_el_sum = float(df["stressed_el_usd"].sum())
        el_increase = stressed_el_sum - base_el_sum

        # Parametric 99% VaR approximation based on volatility of positions
        var_base = base_val * 0.045
        var_stressed = var_base * (1.0 + (severity_ratio * 0.65))

        # Asset class summary
        breakdown = []
        for asset, grp in df.groupby("asset_type"):
            b_val = float(grp["current_mv_usd"].sum())
            s_val = float(grp["stressed_mv_usd"].sum())
            loss = s_val - b_val
            breakdown.append({
                "asset_type": asset,
                "positions_count": int(len(grp)),
                "baseline_mv_usd": round(b_val, 2),
                "stressed_mv_usd": round(s_val, 2),
                "pnl_usd": round(loss, 2),
                "pnl_pct": round((loss / b_val) * 100.0, 2)
            })

        return StressTestResult(
            event_type=event_type,
            impact_score=impact_score,
            baseline_value_usd=base_val,
            stressed_value_usd=stressed_val,
            total_pnl_usd=total_pnl,
            pnl_percentage=pnl_pct,
            baseline_expected_loss_usd=base_el_sum,
            stressed_expected_loss_usd=stressed_el_sum,
            el_increase_usd=el_increase,
            var_99_baseline_usd=var_base,
            var_99_stressed_usd=var_stressed,
            asset_breakdown=breakdown,
            stressed_positions_df=df
        )
