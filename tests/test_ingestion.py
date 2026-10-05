"""
Unit tests for News and Social Data Ingestion Pipelines.
"""

from src.engine import IngestionPipeline, NewsIngester, SocialIngester


def test_news_ingester_local():
    ingester = NewsIngester()
    items = ingester.fetch_local()
    assert len(items) == 40
    sample = items[0]
    assert "headline" in sample
    assert "ticker" in sample
    assert sample["source_type"] == "news"
    assert sample["ticker"] != ""


def test_social_ingester_local():
    ingester = SocialIngester()
    items = ingester.fetch_local()
    assert len(items) == 60
    sample = items[0]
    assert "text" in sample
    assert "ticker" in sample
    assert sample["source_type"] == "social"
    assert "likes" in sample or "engagement_score" in sample


def test_unified_ingestion_pipeline():
    pipeline = IngestionPipeline()
    stream = pipeline.run()
    assert len(stream) == 100
    # Stream must be sorted chronologically
    timestamps = [x["timestamp"] for x in stream if x.get("timestamp")]
    assert timestamps == sorted(timestamps)
