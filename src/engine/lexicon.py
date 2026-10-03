"""
Financial Lexicon and Domain Knowledge Base for Risk Scoring.
Contains curated financial positive/negative vocabulary, event taxonomies,
and sector sensitivity impact weights.
"""

FINANCIAL_LEXICON = {
    # Strong Negative Indicators
    "default": -0.90,
    "bankruptcy": -0.95,
    "insolvency": -0.95,
    "downgrade": -0.75,
    "probe": -0.65,
    "investigation": -0.60,
    "lawsuit": -0.55,
    "litigation": -0.50,
    "restructuring": -0.55,
    "haircut": -0.80,
    "breach": -0.70,
    "antitrust": -0.60,
    "fine": -0.50,
    "penalty": -0.60,
    "delinquency": -0.75,
    "charge-off": -0.70,
    "write-down": -0.70,
    "impairment": -0.65,
    "distressed": -0.85,
    "deficit": -0.50,
    "slump": -0.55,
    "drop": -0.35,
    "decline": -0.35,
    "curtail": -0.40,
    "weakness": -0.45,
    "volatility": -0.30,
    "headwinds": -0.45,
    "disruption": -0.55,

    # Strong Positive Indicators
    "record": 0.50,
    "outperform": 0.70,
    "upgrade": 0.75,
    "beat": 0.60,
    "expansion": 0.55,
    "growth": 0.50,
    "surge": 0.65,
    "rally": 0.60,
    "dividend": 0.45,
    "profitability": 0.60,
    "tailwind": 0.45,
    "resilient": 0.50,
    "resilience": 0.50,
    "breakthrough": 0.70,
    "monetization": 0.50,
    "refinancing": 0.40,
    "partnership": 0.45,
    "acquisition": 0.35,
    "pipeline": 0.30,
    "solvency": 0.60,
    "surplus": 0.55
}

EVENT_KEYWORDS = {
    "Geopolitical": [
        "war", "military", "strait", "conflict", "sanctions", "tariff", "embargo",
        "naval", "geopolitical", "tensions", "shipping", "defense", "missile"
    ],
    "Macroeconomic": [
        "inflation", "federal reserve", "interest rate", "gdp", "recession",
        "unemployment", "pmi", "central bank", "macroeconomic", "yield", "treasury"
    ],
    "Credit Event": [
        "default", "rating", "downgrade", "debt", "bondholders", "credit", "restructuring",
        "distressed", "haircut", "provisions", "charge-off", "maturities", "maturity"
    ],
    "Merger/Acquisition": [
        "acquisition", "merger", "acquire", "takeover", "buyout", "consolidation",
        "divestiture", "joint venture", "definitive agreement"
    ],
    "Regulatory": [
        "antitrust", "investigation", "probe", "regulator", "compliance", "sec",
        "lawsuit", "prior authorization", "commission", "safety audit", "patent litigation"
    ],
    "Product Launch": [
        "launch", "unveil", "shipment", "announces", "facility", "clinical trial",
        "phase 3", "blackwell", "copilot", "chips", "hardware", "pipeline"
    ]
}

EVENT_SEVERITY_WEIGHTS = {
    "Geopolitical": 1.40,
    "Credit Event": 1.50,
    "Regulatory": 1.25,
    "Macroeconomic": 1.20,
    "Merger/Acquisition": 1.10,
    "Product Launch": 1.00
}
