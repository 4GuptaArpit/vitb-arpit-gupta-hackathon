"""
FastAPI REST API Service for exposing structured RiskSignals to downstream applications.
Supports querying signals, filtering by ticker, and real-time ad-hoc text risk scoring.
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.engine import IngestionPipeline, RiskEngine, RiskSignal
from src.modules import TacticalIndexRebalancer, StressTester

app = FastAPI(
    title="RiskPulse AI - Financial Risk Signal Bus",
    description="Real-time structured risk signal endpoint for S&P Global x CRISIL Hackathon 2026",
    version="1.0.0"
)

# Enable CORS for React development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine instances and in-memory caches
engine = RiskEngine()
pipeline = IngestionPipeline()
rebalancer = TacticalIndexRebalancer()
stress_tester = StressTester()
cached_signals: List[RiskSignal] = []


def refresh_signals():
    global cached_signals
    stream = pipeline.run()
    cached_signals = engine.process_stream(stream)


# Preload signals on startup
refresh_signals()


class AnalyzeRequest(BaseModel):
    text: str
    ticker: Optional[str] = "GENERAL"
    publisher: Optional[str] = "Ad-hoc User Input"
    engagement: Optional[int] = 0


@app.get("/health", tags=["System"])
def health_check() -> Dict[str, Any]:
    """System health check and signal cache status."""
    return {
        "status": "healthy",
        "service": "RiskPulse AI Engine",
        "cached_signals_count": len(cached_signals)
    }


@app.get("/signals", tags=["Signals"])
def get_all_signals(
    limit: int = Query(50, ge=1, le=200, description="Number of signals to retrieve"),
    event_type: Optional[str] = Query(None, description="Filter by event category"),
    min_impact: Optional[int] = Query(None, ge=1, le=10, description="Filter by minimum impact severity")
) -> List[Dict[str, Any]]:
    """Retrieve structured risk signals with optional filtering."""
    results = [s.to_dict() for s in cached_signals]

    if event_type:
        results = [r for r in results if r["event_classification"].lower() == event_type.lower()]
    if min_impact:
        results = [r for r in results if r["impact_score"] >= min_impact]

    return results[:limit]


@app.get("/signals/ticker/{symbol}", tags=["Signals"])
def get_signals_by_ticker(symbol: str) -> List[Dict[str, Any]]:
    """Retrieve structured risk signals for a specific company ticker symbol."""
    symbol_clean = symbol.upper()
    matching = [s.to_dict() for s in cached_signals if s.ticker == symbol_clean]
    if not matching:
        raise HTTPException(status_code=404, detail=f"No risk signals found for ticker {symbol_clean}")
    return matching


@app.post("/signals/analyze", tags=["Signals"])
def analyze_text(request: AnalyzeRequest) -> Dict[str, Any]:
    """Analyze ad-hoc financial news or text in real-time and return structured RiskSignal."""
    item = {
        "id": "adhoc_input",
        "ticker": request.ticker.upper() if request.ticker else "GENERAL",
        "source_type": "adhoc_api",
        "publisher": request.publisher,
        "timestamp": "",
        "headline": request.text[:100],
        "text": request.text,
        "engagement_score": request.engagement
    }
    signal = engine.process_item(item)
    return signal.to_dict()


class RebalanceRequest(BaseModel):
    sensitivity_alpha: Optional[float] = 0.35


@app.get("/api/rebalance/state", tags=["Module A: Rebalancer"])
def get_rebalance_state() -> List[Dict[str, Any]]:
    """Retrieve current S&P 100 constituent weights, sectors, and drift."""
    df = rebalancer.get_current_state()
    return df.to_dict(orient="records")


@app.post("/api/rebalance/run", tags=["Module A: Rebalancer"])
def run_rebalance(request: RebalanceRequest) -> Dict[str, Any]:
    """Execute batch rebalancing across active signal stream."""
    rebalancer.sensitivity_alpha = request.sensitivity_alpha or 0.35
    events = rebalancer.rebalance_batch(cached_signals)
    state = rebalancer.get_current_state()
    return {
        "events_count": len(events),
        "recent_events": [e.to_dict() for e in events[-10:]],
        "state": state.to_dict(orient="records")
    }


@app.get("/api/rebalance/backtest", tags=["Module A: Rebalancer"])
def get_rebalance_backtest(sensitivity_alpha: Optional[float] = Query(0.35, ge=0.05, le=1.0)) -> Dict[str, Any]:
    """Calculate quantitative alpha, Sharpe ratio, and MDD vs static benchmark."""
    temp_reb = TacticalIndexRebalancer(sensitivity_alpha=sensitivity_alpha or 0.35)
    return temp_reb.backtest_vs_benchmark(cached_signals)


class StressTestRequest(BaseModel):
    event_type: str
    impact_score: int
    target_sector: Optional[str] = None


@app.post("/api/stress-test/run", tags=["Module B: Stress Tester"])
def run_stress_test(request: StressTestRequest) -> Dict[str, Any]:
    """Execute multi-factor wholesale portfolio stress simulation."""
    target_sec = None if not request.target_sector or request.target_sector.lower() == "none" else request.target_sector
    result = stress_tester.run_stress_test(
        event_type=request.event_type,
        impact_score=request.impact_score,
        target_sector=target_sec
    )
    res_dict = result.to_dict()
    if result.stressed_positions_df is not None:
        res_dict["positions"] = result.stressed_positions_df[[
            "position_id", "asset_type", "counterparty", "sector", "notional_usd",
            "credit_rating", "tenor_years", "current_mv_usd", "stressed_mv_usd", "pnl_usd", "pnl_pct"
        ]].to_dict(orient="records")
    return res_dict


@app.get("/api/stress-test/scenarios", tags=["Module B: Stress Tester"])
def get_stress_scenarios() -> Dict[str, Any]:
    """Retrieve pre-calibrated historical crisis scenario playbook."""
    from src.modules import HISTORICAL_SCENARIOS
    return HISTORICAL_SCENARIOS


@app.post("/api/reports/stress-test/export", tags=["Executive Reports"])
def export_stress_report(
    event_type: str = Query("regulatory_investigation"),
    impact_score: float = Query(7.5, ge=1.0, le=10.0),
    shock_multiplier: float = Query(1.0, ge=0.1, le=5.0)
):
    """Generate and download institutional CRISIL-grade PDF risk memorandum."""
    import tempfile
    from fastapi.responses import FileResponse
    from src.modules import generate_stress_report

    stress_tester = get_stress_tester()
    res = stress_tester.run_stress_test(
        event_type=event_type,
        impact_score=impact_score,
        shock_multiplier=shock_multiplier
    )
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_pdf.close()
    pdf_path = generate_stress_report(res, temp_pdf.name)
    clean_ev = event_type.replace(' ', '_').lower()
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"RiskPulse_Stress_Report_{clean_ev}.pdf"
    )


class SignalReportRequest(BaseModel):
    headline: str
    ticker: str
    event_type: str
    sentiment_score: float
    impact_score: float
    publisher: Optional[str] = "Market Wire"
    key_drivers: Optional[List[str]] = None


@app.post("/api/reports/signal/export", tags=["Executive Reports"])
def export_signal_alert(req: SignalReportRequest):
    """Generate and download institutional 1-page CRISIL Event Credit Alert (PDF)."""
    import tempfile
    from fastapi.responses import FileResponse
    from src.modules import generate_signal_alert_report

    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_pdf.close()
    pdf_path = generate_signal_alert_report(
        headline=req.headline,
        ticker=req.ticker,
        event_type=req.event_type,
        sentiment_score=req.sentiment_score,
        impact_score=req.impact_score,
        publisher=req.publisher or "Market Wire",
        key_drivers=req.key_drivers,
        output_path=temp_pdf.name
    )
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"CRISIL_Credit_Alert_{req.ticker}_{int(req.impact_score)}.pdf"
    )


# Mount React Production Frontend (if built)
from pathlib import Path
from fastapi.staticfiles import StaticFiles

frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


