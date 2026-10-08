import React from 'react';

export default function ContextGuideModal({ isOpen, onClose, activeTab }) {
  if (!isOpen) return null;

  const GUIDES = {
    signals: {
      title: "Real-Time NLP Risk Signals & Event Ingestion",
      tagline: "Unstructured Financial News, Social Chatter & Contagion Radar Engine",
      badge: "S&P 100 Zero-Leakage Pipeline",
      formula: "Severity = \\alpha \\cdot |Sentiment| \\times \\log_{10}(Virality + 10) \\times W_{event}",
      sections: [
        {
          heading: "1. Core Mission & What It Does",
          content: "Ingests streaming real-time financial articles, earnings reports, regulatory releases, and social chatter. Rather than using generic consumer sentiment, it runs domain-adapted financial NLP (FinBERT) to detect subtle financial distress terminology, calculate polarity (-1.0 to +1.0), and classify events into 7 distinct institutional taxonomies (Credit Downgrades, Legal/Regulatory Actions, Earnings Misses, Supply Chain Disruptions, etc.)."
        },
        {
          heading: "2. Contagion & Peer Spillover Radar",
          content: "When you click any individual news card, the Signal Intelligence Dossier reveals the Cross-Asset Contagion Radar. This models how a severe credit or regulatory shock at an epicenter company (e.g. debt liquidity crunch) spills over into sector peers via correlation matrices, triggers flight-to-quality defensive moves into Treasuries/Gold, and impacts Credit Default Swap (CDS) basis spreads."
        },
        {
          heading: "3. How To Use & Test Live",
          content: "• Browse live news cards categorized by Bullish, Bearish, or Critical Severity.\n• Click any card to inspect the Signal Intelligence Dossier with explainable key word drivers.\n• Click 'Export Credit Alert PDF' to generate an institutional 1-page CRISIL credit dossier.\n• Use the What-If Counterfactual Sliders (in Quadrant View or Modal) to stress test severity and sentiment elasticity."
        }
      ]
    },
    rebalance: {
      title: "Module A: Tactical Index Rebalancer & Alpha Backtester",
      tagline: "Quadratic Constrained Portfolio Optimization & Factor Attribution",
      badge: "Basel III & UCITS 5/10/40 Compliant",
      formula: "\\min_w \\frac{1}{2} w^T \\Sigma w - \\lambda w^T \\mu \quad \\text{s.t.} \quad \\sum w_i = 1.0, \\quad w_i \\le 15\\%, \\quad \\sum_{i \\in sector} w_i \\le 30\\%",
      sections: [
        {
          heading: "1. Core Mission & What It Does",
          content: "Translates real-time NLP sentiment signals into tactical portfolio weight adjustments. When negative news impacts a constituent, the engine algorithmically reduces risk exposure while respecting strict institutional guardrails (single-stock cap \\le 15%, sector concentration cap \\le 30%, and maximum 500 bps turnover friction penalty)."
        },
        {
          heading: "2. Mathematical Zero-Sum Invariant & Waterfall",
          content: "Guarantees absolute balance sheet conservation: sum of active inflows must identically equal active outflows (\\sum \\Delta w = 0). The real-time waterfall visualizer demonstrates exact zero cash leakage, ensuring no unallocated phantom capital."
        },
        {
          heading: "3. Brinson-Fachler Factor Attribution (Menchero Linking)",
          content: "Decomposes portfolio excess returns against the S&P 100 benchmark into Allocation Effect (sector timing), Selection Effect (individual stock picking), and Interaction Effect. Uses Menchero logarithmic linking coefficients to mathematically ensure zero compounding drift over multi-day rebalancing cycles."
        },
        {
          heading: "4. How To Use",
          content: "• Click 'Run Rebalance' to execute the quadratic solver on the current signal state.\n• Inspect the Invariant Card and Allocation Waterfall to verify zero-leakage balance conservation.\n• Check the Brinson-Fachler card to audit pure active alpha vs sector beta.\n• Click 'Reset to Benchmark' anytime to restore native index weights."
        }
      ]
    },
    stress: {
      title: "Module B: Wholesale Portfolio Stress Tester",
      tagline: "Multi-Asset Capital Adequacy, FRTB Expected Shortfall & Basel III Governor",
      badge: "RBI Master Direction & CCAR Severely Adverse",
      formula: "Stressed CET1 = \\frac{\\text{CET1}_{\\text{initial}} - \\text{Stressed Loss}}{\\text{RWA}_{\\text{stressed}}}, \\quad ES_{97.5\\%} = \\frac{1}{1-\\alpha} \\int_\\alpha^1 VaR_u(X) du",
      sections: [
        {
          heading: "1. Core Mission & What It Does",
          content: "Simulates severe macroeconomic and liquidity shocks across a wholesale banking loan and corporate bond portfolio ($250M+ notional). Computes Expected Loss (EL = PD \\times LGD \\times EAD), 99% Parametric VaR, and FRTB 97.5% Expected Shortfall under historical and forward-looking stress scenarios."
        },
        {
          heading: "2. Dual-Jurisdiction Basel III & RBI Capital Conservation Governor",
          content: "Implements regulatory capital adequacy thresholds under RBI Master Direction: Minimum CET1 (5.50%) + Capital Conservation Buffer (2.50%) + Domestic Systemically Important Bank (D-SIB) surcharge (0.40%) = 8.40% effective threshold. When CET1 breaches CCB quartiles, it automatically enforces statutory Maximum Distributable Amount (MDA) caps on dividends and bonuses (0%, 20%, 40%, 60%, 100%)."
        },
        {
          heading: "3. Historical Crisis Playbooks",
          content: "Pre-calibrated institutional playbooks allow instantaneous replay of the 2008 Global Financial Crisis (-50% Equity, +450 bps Spreads), the 2020 COVID Flash Crash, 2022-2023 Stagflation, and custom Federal Reserve CCAR Severely Adverse scenarios."
        },
        {
          heading: "4. How To Use",
          content: "• Click any historical scenario card (GFC 2008, COVID 2020, Stagflation, CCAR) to instantly recalculate portfolio capital depletion.\n• Inspect the Basel III Capital Governor card to verify statutory dividend restrictions and CCB quartile status.\n• Click 'Export Stress Report PDF' to download the multi-page C-Suite Capital Adequacy & Risk Committee Memorandum."
        }
      ]
    },
    adhoc: {
      title: "Live Ad-Hoc NLP Signal Analysis Workbench",
      tagline: "Interactive FinBERT Sandbox for Real-Time Financial Text Scoring",
      badge: "Real-Time Scoring Laboratory",
      formula: "Polarity \\in [-1.0, +1.0], \\quad Impact = f(Sentiment, Virality, EventClass)",
      sections: [
        {
          heading: "1. Core Mission & Why It Exists",
          content: "Provides an interactive testing bench for judges and risk officers to verify that the NLP Risk Engine operates in real time on any raw, uncurated financial prose, completely free of hardcoded assumptions."
        },
        {
          heading: "2. Ticker Field vs Text Area Clarification (Credibility Note)",
          content: "• The FinBERT NLP model exclusively scores the text in the main textarea (e.g. debt downgrade, legal lawsuit, earnings beat).\n• The 'Company Ticker' input is an optional routing metadata tag. If an unlisted or custom identifier (e.g. 'XYZ' or personal name) is typed, the system still evaluates the financial severity of the sentence, tagging the generated RiskSignal with that identifier.\n• Valid S&P 100 / NIFTY 50 tickers link directly into the Module A rebalancing basket."
        },
        {
          heading: "3. How To Use",
          content: "• Paste any breaking headline, regulatory filing snippet, or earnings announcement.\n• Adjust the 'Market Engagement / Virality' slider to simulate social velocity.\n• (Optional) Provide a ticker symbol for event attribution.\n• Click 'Score Risk Signal Live' to inspect the calibrated sentiment, event classification confidence (e.g. Credit Event 95%), impact severity (1-10), and the structured JSON payload."
        }
      ]
    }
  };

  const active = GUIDES[activeTab] || GUIDES.signals;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="w-full max-w-3xl bg-slate-900 border border-cyan-500/50 rounded-2xl shadow-2xl overflow-hidden font-mono flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-700/60 font-bold text-sm">
              i
            </span>
            <div>
              <h2 className="text-base font-bold text-slate-100 uppercase tracking-wide">
                {active.title}
              </h2>
              <p className="text-xs text-slate-400">{active.tagline}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
          >
            ✕
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-5 text-xs text-slate-300 leading-relaxed">
          <div className="flex items-center justify-between bg-slate-950/80 px-4 py-2.5 rounded-lg border border-slate-800">
            <span className="text-cyan-400 font-semibold">Regulatory &amp; Engineering Standard:</span>
            <span className="bg-cyan-950 text-cyan-300 px-2 py-0.5 rounded border border-cyan-800 text-[11px]">
              {active.badge}
            </span>
          </div>

          {/* Mathematical / Architectural Specification */}
          <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800/80 font-mono text-cyan-300 text-[11px]">
            <span className="text-[10px] text-slate-500 block uppercase mb-1">Governing Formulation:</span>
            {active.formula}
          </div>

          {/* Detailed Content Sections */}
          {active.sections.map((sec, idx) => (
            <div key={idx} className="space-y-1.5">
              <h4 className="text-sm font-bold text-amber-400 uppercase tracking-wider">
                {sec.heading}
              </h4>
              <p className="text-slate-300 whitespace-pre-line">
                {sec.content}
              </p>
            </div>
          ))}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between text-slate-400 text-[11px]">
          <span>S&amp;P Global &times; CRISIL Campus Hackathon 2026 &bull; Round 3 Case Study</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold transition text-xs"
          >
            Got it, Back to Terminal
          </button>
        </div>
      </div>
    </div>
  );
}
