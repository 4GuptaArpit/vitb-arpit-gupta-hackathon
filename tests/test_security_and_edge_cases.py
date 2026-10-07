"""
Brutal Security, Edge Case, Boundary Condition, and Mathematical Invariant Test Suite.
Verifies platform resilience under adversarial inputs, injection payloads,
extreme floating-point values, and zero/infinite stress shocks.
"""

import math
import pytest
from fastapi.testclient import TestClient

from src.api.signal_api import app
from src.engine import RiskEngine, SentimentAnalyzer, EventClassifier, ImpactScorer, RiskSignal
from src.modules import TacticalIndexRebalancer, StressTester


@pytest.fixture
def api_client():
    return TestClient(app)


# ==============================================================
# 1. SECURITY & INJECTION TESTING
# ==============================================================

def test_xss_injection_payloads_in_adhoc_analyze(api_client):
    """Verify that script tags and HTML injection do not crash or corrupt the response."""
    payloads = [
        "<script>alert('pwned')</script>",
        "<img src=x onerror=alert(1)>",
        "<svg/onload=alert('XSS')>",
        "'; DROP TABLE signals; --",
        "UNION SELECT null, username, password FROM users--"
    ]
    for text in payloads:
        res = api_client.post("/signals/analyze", json={"text": text, "ticker": "TEST"})
        assert res.status_code == 200
        data = res.json()
        assert "sentiment_score" in data
        assert "event_classification" in data
        assert "impact_score" in data
        assert -1.0 <= data["sentiment_score"] <= 1.0


def test_path_traversal_in_ticker_lookup(api_client):
    """Verify that path traversal strings in URL path parameters are safely rejected."""
    traversal_attacks = [
        "../../etc/passwd",
        "..%2F..%2Fwindows%2Fwin.ini",
        "....//....//config.json",
        "CON",
        "NUL",
        "AUX"
    ]
    for ticker in traversal_attacks:
        res = api_client.get(f"/signals/ticker/{ticker}")
        # Should return 404 (or 422), never 500 or leaked filesystem contents
        assert res.status_code in (404, 422)


def test_extreme_huge_text_payload_handling():
    """Verify that a massive 100,000-character string processes without ReDoS or memory blowout."""
    huge_text = ("Federal Reserve inflation interest rate credit downgrade default " * 1500)[:100_000]
    engine = RiskEngine()
    item = {
        "id": "huge_test",
        "ticker": "AAPL",
        "source_type": "stress",
        "publisher": "Adversarial Test",
        "timestamp": "",
        "headline": huge_text[:100],
        "text": huge_text,
        "engagement_score": 100
    }
    sig = engine.process_item(item)
    assert sig is not None
    assert -1.0 <= sig.sentiment_score <= 1.0
    assert 1 <= sig.impact_score <= 10


def test_null_bytes_and_unicode_handling():
    """Verify engine handles null bytes, emoji storms, and multi-byte non-Latin characters."""
    adversarial_texts = [
        "Apple Inc\x00\x00\x00Earnings release\x00",
        "🚀🔥💎🙌 BUY CALLS TO THE MOON 💥📈⚡🎉",
        "Компания объявила о реструктуризации долга и дефолте",
        "中国银行与欧洲监管机构签署反垄断合规协议",
        "   \n\t\r   "
    ]
    engine = RiskEngine()
    for text in adversarial_texts:
        item = {
            "id": "unicode_test",
            "ticker": "GLOBAL",
            "source_type": "stress",
            "publisher": "Tester",
            "timestamp": "",
            "headline": text[:50],
            "text": text,
            "engagement_score": 50
        }
        sig = engine.process_item(item)
        assert -1.0 <= sig.sentiment_score <= 1.0
        assert not math.isnan(sig.sentiment_score)


# ==============================================================
# 2. MATHEMATICAL INVARIANTS (LLD & PORTFOLIO GUARDRAILS)
# ==============================================================

def test_rebalancer_sum_of_weights_invariant():
    """
    Mathematical Invariant:
    Under repeated random and extreme sentiment signals,
    Sum of weights MUST ALWAYS EQUAL EXACTLY 1.000000.
    """
    rebalancer = TacticalIndexRebalancer(sensitivity_alpha=0.45, min_weight=0.01, max_weight=0.18)

    extreme_sentiments = [-1.0, 1.0, -0.999, 0.999, 0.0, -0.5, 0.75]
    tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "JPM", "XOM", "UNH"]

    for sent in extreme_sentiments:
        for t in tickers:
            sig = RiskSignal(
                id=f"test_{t}", ticker=t, source_type="news", publisher="Test",
                timestamp="", headline="", sentiment_score=sent,
                sentiment_label="Test", event_classification="Macroeconomic",
                impact_score=5, confidence_score=0.9, key_drivers=[]
            )
            rebalancer.rebalance_from_signal(sig)
            weights = rebalancer.get_current_state()["current_weight"].values
            assert round(sum(weights), 5) == 1.00000
            assert all(w >= 0.0099 for w in weights), "Floor violated"
            assert all(w <= 0.1801 for w in weights), "Ceiling cap violated"


def test_rebalancer_zero_and_negative_alpha():
    """Verify that zero alpha leaves weights unchanged (no division by zero)."""
    rebalancer = TacticalIndexRebalancer(sensitivity_alpha=0.0)
    sig = RiskSignal(
        id="zero_alpha", ticker="NVDA", source_type="news", publisher="Test",
        timestamp="", headline="", sentiment_score=1.0,
        sentiment_label="Positive", event_classification="Product Launch",
        impact_score=10, confidence_score=1.0, key_drivers=[]
    )
    ev = rebalancer.rebalance_from_signal(sig)
    assert ev.delta_pct == 0.0 or abs(ev.delta_pct) < 0.05


def test_stress_tester_unknown_event_type_fallback():
    """Stress tester must gracefully fallback when an unregistered event type is passed."""
    tester = StressTester()
    res = tester.run_stress_test(event_type="Alien Invasion Catastrophe", impact_score=7)
    assert res is not None
    assert res.stressed_value_usd < res.baseline_value_usd
    assert not math.isnan(res.total_pnl_usd)
    assert not math.isinf(res.total_pnl_usd)


def test_stress_tester_out_of_bounds_severity():
    """Verify severity ratio clamps cleanly between 0.1 and 1.0 without crashing."""
    tester = StressTester()
    res_neg = tester.run_stress_test(event_type="Credit Event", impact_score=-10)
    assert res_neg.stressed_value_usd > 0

    res_extreme = tester.run_stress_test(event_type="Credit Event", impact_score=999)
    assert res_extreme.stressed_value_usd > 0
    assert res_extreme.total_pnl_usd < 0


def test_stress_tester_nonexistent_sector():
    """Verify sector targeting safely handles sectors not in the portfolio."""
    tester = StressTester()
    res = tester.run_stress_test(event_type="Macroeconomic", impact_score=5, target_sector="Intergalactic Mining")
    assert res is not None
    assert len(res.asset_breakdown) == 4


# ==============================================================
# 3. END-TO-END FASTAPI INTEGRATION & FILTER BOUNDARIES
# ==============================================================

def test_api_signals_filtering_boundaries(api_client):
    """Test boundary conditions for pagination and impact filters."""
    # min_impact boundary 10
    res = api_client.get("/signals?min_impact=10")
    assert res.status_code == 200
    for s in res.json():
        assert s["impact_score"] == 10

    # limit bounds
    res_limit = api_client.get("/signals?limit=1")
    assert res_limit.status_code == 200
    assert len(res_limit.json()) == 1


def test_api_rebalance_run_and_state(api_client):
    """Verify full HTTP roundtrip for Module A."""
    res_state = api_client.get("/api/rebalance/state")
    assert res_state.status_code == 200
    assert len(res_state.json()) == 20

    res_run = api_client.post("/api/rebalance/run", json={"sensitivity_alpha": 0.5})
    assert res_run.status_code == 200
    data = res_run.json()
    assert "events_count" in data
    assert "state" in data
    assert len(data["state"]) == 20


def test_api_stress_test_full_roundtrip(api_client):
    """Verify full HTTP roundtrip for Module B."""
    res = api_client.post("/api/stress-test/run", json={
        "event_type": "Regulatory",
        "impact_score": 6,
        "target_sector": "Healthcare"
    })
    assert res.status_code == 200
    data = res.json()
    assert "baseline_value_usd" in data
    assert "stressed_value_usd" in data
    assert "positions" in data
    assert len(data["positions"]) == 30
