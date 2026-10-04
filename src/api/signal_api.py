"""
FastAPI REST API Service for exposing structured RiskSignals to downstream applications.
Supports querying signals, filtering by ticker, and real-time ad-hoc text risk scoring.
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from src.engine import IngestionPipeline, RiskEngine, RiskSignal

app = FastAPI(
    title="RiskPulse AI - Financial Risk Signal Bus",
    description="Real-time structured risk signal endpoint for S&P Global x CRISIL Hackathon 2026",
    version="1.0.0"
)

# Global engine instance and in-memory signal cache
engine = RiskEngine()
pipeline = IngestionPipeline()
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
