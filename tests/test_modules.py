"""
Unit tests for Downstream Modules (Module A: Rebalancer, Module B: Stress Tester).
"""

from src.engine import RiskSignal
from src.modules import StressTester, TacticalIndexRebalancer


def test_module_a_rebalancer_guardrails():
    rebalancer = TacticalIndexRebalancer(sensitivity_alpha=0.35, min_weight=0.01, max_weight=0.18)

    # Initial basket state must sum to 1.0
    state_init = rebalancer.get_current_state()
    assert round(state_init["current_weight"].sum(), 4) == 1.0000

    # Test positive sentiment rebalance
    bull_signal = RiskSignal(
        id="sig_bull", ticker="NVDA", source_type="news", publisher="Bloomberg",
        timestamp="2026-09-28T12:00:00Z", headline="Surge in Blackwell GPU demand",
        sentiment_score=0.80, sentiment_label="Positive", event_classification="Product Launch",
        impact_score=8, confidence_score=0.9, key_drivers=[]
    )
    ev_bull = rebalancer.rebalance_from_signal(bull_signal)
    assert ev_bull is not None
    assert ev_bull.delta_pct > 0.0

    # Test negative sentiment rebalance
    bear_signal = RiskSignal(
        id="sig_bear", ticker="AAPL", source_type="news", publisher="Reuters",
        timestamp="2026-09-28T12:05:00Z", headline="Antitrust probe fine risk",
        sentiment_score=-0.75, sentiment_label="Negative", event_classification="Regulatory",
        impact_score=6, confidence_score=0.9, key_drivers=[]
    )
    ev_bear = rebalancer.rebalance_from_signal(bear_signal)
    assert ev_bear is not None
    assert ev_bear.delta_pct < 0.0

    # After multiple rebalances, total weight must strictly sum to 1.0
    final_state = rebalancer.get_current_state()
    assert round(final_state["current_weight"].sum(), 4) == 1.0000

    # Concentration guardrails must hold
    assert final_state["current_weight"].min() >= 0.010
    assert final_state["current_weight"].max() <= 0.180


def test_module_b_stress_tester():
    stress_tester = StressTester()
    res = stress_tester.run_stress_test(event_type="Geopolitical", impact_score=9)

    assert res.baseline_value_usd > 1_000_000_000.0  # > $1.0B portfolio
    assert res.stressed_value_usd < res.baseline_value_usd
    assert res.total_pnl_usd < 0.0                   # Drawdown
    assert res.el_increase_usd > 0.0                 # Expected loss increases
    assert res.var_99_stressed_usd > res.var_99_baseline_usd
    assert len(res.asset_breakdown) == 4             # 4 asset classes: Loans, IG Bonds, HY Bonds, CDS
    assert res.stressed_positions_df is not None


def test_pdf_report_generator(tmp_path):
    from src.modules import StressTester, generate_stress_report
    from pathlib import Path

    stress_tester = StressTester()
    res = stress_tester.run_stress_test(event_type="macro_recession", impact_score=8.5)
    pdf_out = str(tmp_path / "test_report.pdf")
    generated_path = generate_stress_report(res, pdf_out)

    assert Path(generated_path).exists()
    assert Path(generated_path).stat().st_size > 1000  # valid PDF generated


def test_tactical_rebalancer_backtest():
    rebalancer = TacticalIndexRebalancer()
    signals = [
        RiskSignal(
            id=f"sig_{i}", ticker="NVDA" if i % 2 == 0 else "AAPL",
            source_type="news", publisher="Reuters", timestamp="2026-09-28T12:00:00Z",
            headline="Sample headline", sentiment_score=0.6 if i % 2 == 0 else -0.5,
            sentiment_label="Positive" if i % 2 == 0 else "Negative",
            event_classification="Earnings", impact_score=7, confidence_score=0.9, key_drivers=[]
        )
        for i in range(10)
    ]
    bt = rebalancer.backtest_vs_benchmark(signals)
    assert "strategy_cumulative_return_pct" in bt
    assert "benchmark_cumulative_return_pct" in bt
    assert "alpha_bps" in bt
    assert "strategy_sharpe" in bt
    assert len(bt["time_series"]) == 10

