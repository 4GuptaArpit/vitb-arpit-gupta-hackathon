"""
Core AI/NLP Risk Engine for Financial Signal Extraction.
Extracts:
1. Sentiment Score [-1.0 to 1.0]
2. Event Classification (Geopolitical, Macro, Credit, M&A, Regulatory, Product)
3. Impact Score [1 to 10]
"""

import logging
import math
import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

from .lexicon import EVENT_KEYWORDS, EVENT_SEVERITY_WEIGHTS, FINANCIAL_LEXICON

logger = logging.getLogger(__name__)


@dataclass
class RiskSignal:
    id: str
    ticker: str
    source_type: str
    publisher: str
    timestamp: str
    headline: str
    sentiment_score: float      # -1.0 to +1.0
    sentiment_label: str        # Positive, Negative, Neutral
    event_classification: str   # Categorical label
    impact_score: int           # 1 to 10 severity
    confidence_score: float     # 0.0 to 1.0
    key_drivers: List[str]      # Top words / evidence driving signal

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SentimentAnalyzer:
    """Hybrid sentiment engine: FinBERT with domain lexicon ensemble fallback."""

    def __init__(self, use_transformer: bool = False):
        self.use_transformer = use_transformer
        self.pipeline = None

        if self.use_transformer:
            try:
                from transformers import pipeline
                self.pipeline = pipeline(
                    "sentiment-analysis",
                    model="ProsusAI/finbert",
                    tokenizer="ProsusAI/finbert"
                )
                logger.info("FinBERT transformer pipeline initialized successfully.")
            except Exception as e:
                logger.warning("FinBERT unavailable (%s), using rule-based financial lexicon.", e)
                self.pipeline = None

    def analyze(self, text: str) -> Tuple[float, str, List[str]]:
        """Compute sentiment score in [-1.0, 1.0], label, and driving tokens."""
        lower_text = text.lower()
        tokens = re.findall(r"\b[a-z\-]+\b", lower_text)
        
        lexicon_score = 0.0
        drivers = []
        for token in tokens:
            if token in FINANCIAL_LEXICON:
                w = FINANCIAL_LEXICON[token]
                lexicon_score += w
                drivers.append(f"{token} ({w:+.2f})")

        # Normalize score via tanh-like scaling
        if drivers:
            normalized_score = math.tanh(lexicon_score / 1.5)
        else:
            normalized_score = 0.0

        # Optional transformer blend if available
        if self.pipeline:
            try:
                res = self.pipeline(text[:512])[0]
                label = res["label"].lower()
                conf = float(res["score"])
                t_score = conf if label == "positive" else (-conf if label == "negative" else 0.0)
                normalized_score = round(0.6 * t_score + 0.4 * normalized_score, 3)
            except Exception:
                pass

        normalized_score = max(-1.0, min(1.0, round(normalized_score, 3)))
        if normalized_score > 0.15:
            sentiment_label = "Positive"
        elif normalized_score < -0.15:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"

        return normalized_score, sentiment_label, drivers[:4]


class EventClassifier:
    """Classifies financial events into standard S&P/CRISIL risk categories."""

    def __init__(self):
        self.categories = list(EVENT_KEYWORDS.keys())

    def classify(self, text: str, hint: Optional[str] = None) -> Tuple[str, float]:
        """Classify event using keyword matching and context weights."""
        if hint and hint in self.categories:
            return hint, 0.95

        lower_text = text.lower()
        scores = {cat: 0.0 for cat in self.categories}

        for cat, keywords in EVENT_KEYWORDS.items():
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", lower_text):
                    scores[cat] += 1.0

        best_cat = max(scores, key=scores.get)
        total_hits = sum(scores.values())

        if total_hits > 0:
            confidence = min(0.95, round(scores[best_cat] / total_hits, 2))
        else:
            best_cat = "Macroeconomic"
            confidence = 0.50

        return best_cat, confidence


class ImpactScorer:
    """Calculates event impact severity score from 1 to 10."""

    @staticmethod
    def calculate(sentiment_score: float, event_type: str, engagement: int = 0) -> int:
        """
        Calculates severity based on sentiment magnitude, event category,
        and market engagement virality.
        """
        magnitude = abs(sentiment_score)
        base_weight = EVENT_SEVERITY_WEIGHTS.get(event_type, 1.0)

        # Baseline impact scale from 1 to 7 based on sentiment magnitude & event type
        raw_score = 1.0 + (magnitude * 5.0 * base_weight)

        # High engagement / severe events scale up to 10
        if engagement > 200:
            raw_score += 1.5
        elif engagement > 100:
            raw_score += 0.8

        final_score = int(round(raw_score))
        return max(1, min(10, final_score))


class RiskEngine:
    """Master NLP Engine orchestrating ingestion items into structured risk signals."""

    def __init__(self, use_transformer: bool = False):
        self.sentiment_analyzer = SentimentAnalyzer(use_transformer=use_transformer)
        self.classifier = EventClassifier()
        self.impact_scorer = ImpactScorer()

    def process_item(self, item: Dict[str, Any]) -> RiskSignal:
        """Processes a single text item into a validated RiskSignal."""
        text = item.get("text", "")
        hint = item.get("event_hint")
        engagement = item.get("engagement_score", 0)

        sentiment_score, sentiment_label, drivers = self.sentiment_analyzer.analyze(text)
        event_cat, confidence = self.classifier.classify(text, hint=hint)
        impact = self.impact_scorer.calculate(sentiment_score, event_cat, engagement=engagement)

        return RiskSignal(
            id=item.get("id", "sig_unknown"),
            ticker=item.get("ticker", "MARKET"),
            source_type=item.get("source_type", "unstructured"),
            publisher=item.get("publisher", "Unknown"),
            timestamp=item.get("timestamp", ""),
            headline=item.get("headline", ""),
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            event_classification=event_cat,
            impact_score=impact,
            confidence_score=confidence,
            key_drivers=drivers
        )

    def process_stream(self, stream: List[Dict[str, Any]]) -> List[RiskSignal]:
        """Processes a batch stream of items."""
        return [self.process_item(item) for item in stream]
