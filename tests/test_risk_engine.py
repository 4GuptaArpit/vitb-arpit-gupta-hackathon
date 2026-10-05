"""
Unit tests for AI/NLP Risk Engine (Sentiment, Event Classification, Impact Scoring).
"""

from src.engine import EventClassifier, ImpactScorer, RiskEngine, SentimentAnalyzer


def test_sentiment_analyzer_positive():
    analyzer = SentimentAnalyzer(use_transformer=False)
    score, label, drivers = analyzer.analyze("Company reports record earnings growth and strong dividend expansion")
    assert score > 0.20
    assert label == "Positive"
    assert len(drivers) > 0


def test_sentiment_analyzer_negative():
    analyzer = SentimentAnalyzer(use_transformer=False)
    score, label, drivers = analyzer.analyze("Bondholders face default risk and severe debt restructuring haircut")
    assert score < -0.30
    assert label == "Negative"
    assert len(drivers) > 0


def test_event_classifier():
    classifier = EventClassifier()
    cat, conf = classifier.classify("Escalating naval military conflict tensions disrupt shipping lanes")
    assert cat == "Geopolitical"
    assert conf > 0.50

    cat_macro, _ = classifier.classify("Central bank warns inflation and interest rate policy will stay restrictive")
    assert cat_macro == "Macroeconomic"


def test_impact_scorer():
    scorer = ImpactScorer()
    # High negative sentiment + high severity event -> impact >= 7
    high_impact = scorer.calculate(sentiment_score=-0.85, event_type="Credit Event", engagement=250)
    assert 7 <= high_impact <= 10

    # Mild positive sentiment -> moderate impact
    low_impact = scorer.calculate(sentiment_score=0.20, event_type="Product Launch", engagement=10)
    assert 1 <= low_impact <= 5


def test_risk_engine_end_to_end():
    engine = RiskEngine()
    item = {
        "id": "t_01",
        "ticker": "AAPL",
        "source_type": "news",
        "publisher": "Reuters",
        "timestamp": "2026-09-28T10:00:00Z",
        "headline": "EU regulators launch formal antitrust probe against tech giant",
        "text": "EU regulators launch formal antitrust probe against tech giant with potential heavy fines.",
        "engagement_score": 120
    }
    sig = engine.process_item(item)
    assert sig.ticker == "AAPL"
    assert sig.sentiment_score < 0.0
    assert sig.event_classification == "Regulatory"
    assert 1 <= sig.impact_score <= 10
    assert sig.to_dict()["ticker"] == "AAPL"
