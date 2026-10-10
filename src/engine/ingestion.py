"""
Multi-Source Data Ingestion Engine for Financial News and Social Media Feeds.
Provides modular ingestion adapters and an orchestrator pipeline.
"""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class NewsIngester:
    """Ingester for formal financial news feeds (Reuters, Bloomberg, etc.)."""

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = Path(data_path) if data_path else Path("data/news_feed_sample.json")

    def fetch_local(self) -> List[Dict[str, Any]]:
        """Load curated news items from local JSON archive."""
        if not self.data_path.exists():
            logger.warning("News data path %s does not exist", self.data_path)
            return []
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw_items = json.load(f)
        
        normalized: List[Dict[str, Any]] = []
        for item in raw_items:
            normalized.append({
                "id": item.get("id"),
                "source_type": "news",
                "publisher": item.get("source", "Unknown"),
                "timestamp": item.get("timestamp", datetime.now(timezone.utc).isoformat()),
                "ticker": item.get("ticker", "GENERAL"),
                "headline": item.get("headline", ""),
                "text": f"{item.get('headline', '')}. {item.get('body', '')}".strip(),
                "event_hint": item.get("event_hint", "General")
            })
        return normalized

    def fetch_live_headlines(self, ticker: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch real-time headlines using yfinance if available,
        with graceful fallback to empty list.
        """
        try:
            import yfinance as yf
            t = yf.Ticker(ticker)
            raw_news = t.get_news()
            items = []
            for idx, entry in enumerate(raw_news[:count]):
                title = entry.get("title", "")
                publisher = entry.get("publisher", "Yahoo Finance")
                ts = entry.get("providerPublishTime")
                dt_str = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat() if ts else datetime.now(timezone.utc).isoformat()
                items.append({
                    "id": f"live_{ticker}_{idx}",
                    "source_type": "news_live",
                    "publisher": publisher,
                    "timestamp": dt_str,
                    "ticker": ticker.upper(),
                    "headline": title,
                    "text": title,
                    "event_hint": "General"
                })
            return items
        except Exception as e:
            logger.warning("Live news fetch for %s encountered notice: %s", ticker, e)
            return []


class SocialIngester:
    """Ingester for retail and institutional microblog commentary."""

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = Path(data_path) if data_path else Path("data/social_feed_sample.json")

    def fetch_local(self) -> List[Dict[str, Any]]:
        """Load microblog posts with cashtag normalization."""
        if not self.data_path.exists():
            logger.warning("Social data path %s does not exist", self.data_path)
            return []
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw_items = json.load(f)

        normalized: List[Dict[str, Any]] = []
        cashtag_pattern = re.compile(r"\$([A-Z]{1,5})\b")

        for item in raw_items:
            text = item.get("text", "")
            ticker = item.get("ticker")
            if not ticker:
                match = cashtag_pattern.search(text)
                ticker = match.group(1) if match else "MARKET"

            normalized.append({
                "id": item.get("id"),
                "source_type": "social",
                "publisher": item.get("platform", "Microblog"),
                "timestamp": item.get("timestamp", datetime.now(timezone.utc).isoformat()),
                "ticker": ticker.upper(),
                "headline": text[:80] + "..." if len(text) > 80 else text,
                "text": text,
                "user_reputation": item.get("user_reputation", "standard"),
                "engagement_score": item.get("likes", 0)
            })
        return normalized


class IngestionPipeline:
    """Orchestrates multi-source ingestion into a single chronological stream."""

    def __init__(self, news_path: Optional[str] = None, social_path: Optional[str] = None):
        self.news_ingester = NewsIngester(news_path)
        self.social_ingester = SocialIngester(social_path)

    def run(self, include_live: bool = False, live_tickers: Optional[List[str]] = None, newest_first: bool = False) -> List[Dict[str, Any]]:
        """Execute unified ingestion across local news, social, and optional live feeds."""
        stream: List[Dict[str, Any]] = []
        stream.extend(self.news_ingester.fetch_local())
        stream.extend(self.social_ingester.fetch_local())

        if include_live and live_tickers:
            for ticker in live_tickers:
                stream.extend(self.news_ingester.fetch_live_headlines(ticker))

        # Sort chronologically
        stream.sort(key=lambda x: x.get("timestamp", ""), reverse=newest_first)
        return stream
