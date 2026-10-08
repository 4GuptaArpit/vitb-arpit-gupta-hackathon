import React, { useEffect } from 'react'
import { X, TrendingDown, TrendingUp, AlertTriangle, ShieldAlert, Cpu, ArrowRight, Activity, FileText, Download, Network } from 'lucide-react'


// Realistic institutional transmission channel mappings
const TRANSMISSION_PROFILES = {
  'Regulatory': {
    operational: 'Scrutiny on compliance or antitrust threatens high-margin recurring revenues, risking multi-billion regulatory fines and structural operational remedies.',
    rebalanceTilt: 'Target constituent weight down-tilted; capital redistributed to defensive sectors (Consumer/Energy) to maintain 100% basket balance.',
    creditSpread: '+35 to +65 bps spread widening across senior unsecured debt; rating watch negative.',
    channelIcon: ShieldAlert,
    channelColor: 'text-amber-400'
  },
  'Credit Event': {
    operational: 'Counterparty default risk or liquidity strain increases debt refinancing costs and strains free cash flow covenants.',
    rebalanceTilt: 'Aggressive de-weighting to avoid tail risk drawdowns; trigger protective concentration floor clamps.',
    creditSpread: '+120 to +250 bps CDS widening; immediate PD migration to lower credit tiers.',
    channelIcon: AlertTriangle,
    channelColor: 'text-rose-400'
  },
  'Geopolitical': {
    operational: 'Supply chain friction, trade sanctions, or regional conflict disrupt cross-border logistics and inflate input commodity costs.',
    rebalanceTilt: 'Global cyclical exposure trimmed; allocation shifted to domestic staple defensives.',
    creditSpread: 'Cross-border loan provisions increased; sovereign and corporate CDS basis risk expands.',
    channelIcon: AlertTriangle,
    channelColor: 'text-orange-400'
  },
  'Macroeconomic': {
    operational: 'Interest rate trajectory, inflation prints, or monetary policy shifts alter capital expenditure discount rates.',
    rebalanceTilt: 'Systemic beta rebalancing; duration-sensitive growth stocks adjusted versus value cash cows.',
    creditSpread: 'Yield curve steepening/flattening impacts duration MTM markdowns across investment grade debt.',
    channelIcon: Activity,
    channelColor: 'text-purple-400'
  },
  'Earnings': {
    operational: 'Variance in quarterly revenue, EPS, or guidance recalibrates forward price-to-earnings multiples.',
    rebalanceTilt: 'High-frequency momentum tilt applied; positive surprises receive proportional overweighting.',
    creditSpread: 'Leverage coverage ratios reassessed; EBITDA covenant headroom adjusted.',
    channelIcon: Activity,
    channelColor: 'text-sky-400'
  },
  'Product Launch': {
    operational: 'Commercial rollout or technological innovation drives enterprise market share expansion and pricing power.',
    rebalanceTilt: 'Pro-cyclical weight boost within concentration ceiling (max 18.0%).',
    creditSpread: 'Credit outlook stabilized; tightens secondary market bond yields.',
    channelIcon: Cpu,
    channelColor: 'text-emerald-400'
  }
}

export default function SignalDetailModal({ signal, onClose, onNavigateTab }) {
  const [whatIfImpact, setWhatIfImpact] = React.useState(signal?.impact_score || 5)
  const [whatIfSentiment, setWhatIfSentiment] = React.useState(signal?.sentiment_score || 0.0)

  React.useEffect(() => {
    if (signal) {
      setWhatIfImpact(signal.impact_score)
      setWhatIfSentiment(signal.sentiment_score)
    }
  }, [signal])

  const [exportingPdf, setExportingPdf] = React.useState(false)

  async function handleDownloadPdf() {
    if (!signal) return
    try {
      setExportingPdf(true)
      const res = await fetch('/api/reports/signal/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          headline: signal.headline,
          ticker: signal.ticker,
          event_type: signal.event_classification,
          sentiment_score: whatIfSentiment,
          impact_score: whatIfImpact,
          publisher: signal.publisher || 'Market Wire',
          key_drivers: signal.key_drivers
        })
      })
      if (!res.ok) throw new Error('Failed to generate PDF')
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `CRISIL_Credit_Alert_${signal.ticker}_${whatIfImpact}.pdf`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (e) {
      console.error(e)
      alert('Could not download PDF alert.')
    } finally {
      setExportingPdf(false)
    }
  }

  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  if (!signal) return null

  const profile = TRANSMISSION_PROFILES[signal.event_classification] || {
    operational: 'Headline news triggers market reassessment of forward cash flows and risk premia.',
    rebalanceTilt: 'Constituent weight adjusted proportionally based on sensitivity alpha and sentiment magnitude.',
    creditSpread: 'Credit spreads and default probabilities calibrated to systemic severity.',
    channelIcon: Activity,
    channelColor: 'text-sky-400'
  }

  const isPositive = whatIfSentiment >= 0.0
  const ChannelIcon = profile.channelIcon

  // Dynamic counterfactual calculations
  const estimatedDelta = (whatIfSentiment * (whatIfImpact / 10.0) * 1.2).toFixed(2)
  const spreadBps = Math.round(Math.abs(whatIfSentiment) * whatIfImpact * 8.5)
  const pdMultiplier = (1.0 + (Math.max(0, -whatIfSentiment) * (whatIfImpact / 10.0) * 1.5)).toFixed(2)
  const isModified = whatIfImpact !== signal.impact_score || Math.abs(whatIfSentiment - signal.sentiment_score) > 0.01


  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="bg-[#0b101d] border border-slate-700/80 rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl shadow-sky-950/40 flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header Bar */}
        <div className="p-5 border-b border-slate-800 flex items-start justify-between bg-slate-900/60 sticky top-0 z-10 backdrop-blur">
          <div className="flex items-center space-x-3">
            <span className="font-mono text-base font-black px-3 py-1 rounded bg-sky-500/10 border border-sky-500/30 text-sky-400">
              {signal.ticker}
            </span>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 font-semibold border border-slate-700">
              {signal.event_classification}
            </span>
            <span className="text-xs text-slate-400 font-mono">
              Source: {signal.publisher} • {signal.timestamp ? signal.timestamp.slice(0, 16).replace('T', ' ') : 'Live Stream'}
            </span>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-6">
          {/* Main Headline & Sentiment Scorecard */}
          <div className="bg-[#0f172a]/90 p-4 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-start justify-between gap-4">
              <h3 className="text-sm font-semibold text-slate-100 leading-snug">
                {signal.headline}
              </h3>
              <div className="flex items-center space-x-2 shrink-0">
                <div className={`px-3 py-1 rounded-lg font-mono font-bold text-xs flex items-center space-x-1 border ${
                  isPositive 
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' 
                    : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                }`}>
                  {isPositive ? <TrendingUp className="w-3.5 h-3.5 mr-1" /> : <TrendingDown className="w-3.5 h-3.5 mr-1" />}
                  <span>{isPositive ? `+${signal.sentiment_score.toFixed(2)}` : signal.sentiment_score.toFixed(2)}</span>
                  <span className="text-[10px] text-slate-400 font-normal ml-1">({signal.sentiment_label})</span>
                </div>
                <div className="px-2.5 py-1 rounded-lg font-mono font-bold text-xs bg-slate-800 text-amber-300 border border-slate-700">
                  Severity {signal.impact_score}/10
                </div>
              </div>
            </div>

            <div className="text-[11px] text-slate-400 flex items-center space-x-3 pt-1 border-t border-slate-800/80">
              <span>Confidence: <strong className="text-slate-200">{Math.round((signal.confidence_score || 0.88) * 100)}%</strong></span>
              <span>•</span>
              <span>Model: <strong className="text-sky-400">FinBERT Hybrid Risk Engine</strong></span>
              <span>•</span>
              <span>Signal ID: <code className="text-slate-400">{signal.id}</code></span>
            </div>
          </div>

          {/* Interactive What-If Counterfactual Simulator */}
          <div className="p-4 bg-gradient-to-r from-slate-900/90 via-[#0d1729] to-slate-900/90 border border-sky-500/30 rounded-xl space-y-3 shadow-inner">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-sky-400 animate-pulse" />
                <span className="text-xs font-bold text-sky-300 uppercase tracking-wider">
                  Interactive "What-If" Counterfactual Simulator
                </span>
                {isModified && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 font-semibold">
                    Simulating Scenario
                  </span>
                )}
              </div>
              {isModified && (
                <button
                  onClick={() => {
                    setWhatIfImpact(signal.impact_score)
                    setWhatIfSentiment(signal.sentiment_score)
                  }}
                  className="text-[11px] text-slate-400 hover:text-sky-300 underline underline-offset-2 transition"
                >
                  Reset to Baseline
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
              {/* Severity Slider */}
              <div className="space-y-1.5 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Simulated Severity:</span>
                  <span className="font-mono font-bold text-amber-400">{whatIfImpact}/10</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="1"
                  value={whatIfImpact}
                  onChange={(e) => setWhatIfImpact(Number(e.target.value))}
                  className="w-full accent-amber-400 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
                />
                <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                  <span>1 (Mild)</span>
                  <span>5 (Moderate)</span>
                  <span>10 (Catastrophic)</span>
                </div>
              </div>

              {/* Sentiment Polarity Slider */}
              <div className="space-y-1.5 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Simulated Sentiment:</span>
                  <span className={`font-mono font-bold ${whatIfSentiment >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {whatIfSentiment >= 0 ? `+${whatIfSentiment.toFixed(2)}` : whatIfSentiment.toFixed(2)}
                  </span>
                </div>
                <input
                  type="range"
                  min="-1.0"
                  max="1.0"
                  step="0.05"
                  value={whatIfSentiment}
                  onChange={(e) => setWhatIfSentiment(Number(e.target.value))}
                  className={`w-full cursor-pointer h-1.5 bg-slate-800 rounded-lg ${whatIfSentiment >= 0 ? 'accent-emerald-400' : 'accent-rose-400'}`}
                />
                <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                  <span>-1.0 (Distressed)</span>
                  <span>0.0 (Neutral)</span>
                  <span>+1.0 (Euphoric)</span>
                </div>
              </div>
            </div>

            {/* Recalculated Impact Badges */}
            <div className="grid grid-cols-3 gap-2 pt-1 text-center font-mono">
              <div className="bg-slate-950/80 p-2 rounded-lg border border-slate-800">
                <div className="text-[10px] text-slate-500 uppercase">Simulated Δ Weight</div>
                <div className={`text-xs font-bold ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {isPositive ? `+${estimatedDelta}%` : `${estimatedDelta}%`}
                </div>
              </div>
              <div className="bg-slate-950/80 p-2 rounded-lg border border-slate-800">
                <div className="text-[10px] text-slate-500 uppercase">Spread Widening</div>
                <div className="text-xs font-bold text-amber-400">
                  +{spreadBps} bps
                </div>
              </div>
              <div className="bg-slate-950/80 p-2 rounded-lg border border-slate-800">
                <div className="text-[10px] text-slate-500 uppercase">PD Multiplier</div>
                <div className="text-xs font-bold text-purple-400">
                  {pdMultiplier}x
                </div>
              </div>
            </div>
          </div>

          {/* Section: Why & How It Impacts (Transmission Channels) */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
              <ChannelIcon className={`w-4 h-4 ${profile.channelColor}`} />
              <span>Risk Transmission Mechanism (Why & How It Impacts)</span>
            </div>


            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {/* Channel 1: Operational */}
              <div className="p-3.5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1.5">
                <div className="text-[11px] font-semibold text-slate-300 flex items-center justify-between">
                  <span>1. Corporate Cash-Flow</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">Fundamental</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {profile.operational}
                </p>
              </div>

              {/* Channel 2: Module A Index */}
              <div className="p-3.5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1.5">
                <div className="text-[11px] font-semibold text-sky-300 flex items-center justify-between">
                  <span>2. Module A: S&P Basket</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-800/50">
                    Est. {isPositive ? `+${estimatedDelta}%` : `${estimatedDelta}%`}
                  </span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {profile.rebalanceTilt}
                </p>
              </div>

              {/* Channel 3: Module B Credit */}
              <div className="p-3.5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1.5">
                <div className="text-[11px] font-semibold text-amber-300 flex items-center justify-between">
                  <span>3. Module B: Wholesale Credit</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800/50">Credit MTM</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {profile.creditSpread}
                </p>
              </div>
            </div>
          </div>

          {/* Section: Cross-Asset Contagion & Peer Spillover Radar */}
          <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-2.5">
            <div className="flex items-center justify-between text-xs font-bold text-slate-300 uppercase tracking-wider">
              <span className="flex items-center space-x-1.5">
                <Network className="w-3.5 h-3.5 text-sky-400" />
                <span>Cross-Asset Contagion & Peer Spillover Radar</span>
              </span>
              <span className="text-[10px] text-slate-500 font-mono">2nd-Order Beta Propagation</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 pt-1 font-mono text-xs">
              <div className="p-2.5 rounded-lg bg-slate-950 border border-sky-500/30">
                <div className="text-[10px] text-sky-400 uppercase font-sans font-semibold">Shock Epicenter</div>
                <div className="text-sm font-bold text-white mt-0.5">{signal.ticker}</div>
                <div className={`text-[11px] ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
                  Direct: {whatIfSentiment >= 0 ? `+${whatIfSentiment.toFixed(2)}` : whatIfSentiment.toFixed(2)}
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                <div className="text-[10px] text-slate-400 uppercase font-sans font-semibold">Sector Peer Drag</div>
                <div className="text-sm font-bold text-slate-200 mt-0.5">
                  {signal.ticker === 'NVDA' ? 'AMD / INTC' : signal.ticker === 'AAPL' ? 'MSFT / GOOGL' : 'SECTOR PEERS'}
                </div>
                <div className="text-[11px] text-amber-400">
                  Drag: {(whatIfSentiment * 0.45).toFixed(2)}
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                <div className="text-[10px] text-slate-400 uppercase font-sans font-semibold">Defensive Inflows</div>
                <div className="text-sm font-bold text-slate-200 mt-0.5">XOM / PG / JNJ</div>
                <div className="text-[11px] text-emerald-400">
                  Flight-to-Quality
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                <div className="text-[10px] text-slate-400 uppercase font-sans font-semibold">Wholesale CDS Basis</div>
                <div className="text-sm font-bold text-slate-200 mt-0.5">+{spreadBps} bps</div>
                <div className="text-[11px] text-purple-400">
                  {pdMultiplier}x PD Shock
                </div>
              </div>
            </div>
          </div>

          {/* Section: NLP Explainability (XAI) Drivers */}
          {signal.key_drivers && signal.key_drivers.length > 0 && (
            <div className="p-4 bg-slate-900/40 border border-slate-800/80 rounded-xl space-y-2">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                <span className="flex items-center space-x-1.5">
                  <FileText className="w-3.5 h-3.5 text-sky-400" />
                  <span>Explainable AI (XAI) Sentiment Attribution</span>
                </span>
                <span className="text-[10px] text-slate-500">Domain-Calibrated Lexicon Weights</span>
              </div>
              <div className="flex flex-wrap gap-2 pt-1">
                {signal.key_drivers.map((driver, idx) => (
                  <span 
                    key={idx} 
                    className="font-mono text-xs px-2.5 py-1 rounded-lg bg-slate-800/90 border border-slate-700 text-slate-200 flex items-center space-x-1"
                  >
                    <span className="text-sky-400">#</span>
                    <span>{driver}</span>
                  </span>
                ))}
              </div>
              <p className="text-[11px] text-slate-500 pt-1 leading-relaxed">
                Tokens extracted and weighted through financial sentiment dictionaries calibrated for corporate disclosure and earnings narrative variance.
              </p>
            </div>
          )}
        </div>

        {/* Action Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/80 flex items-center justify-between sticky bottom-0 z-10 backdrop-blur">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            Close
          </button>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleDownloadPdf}
              disabled={exportingPdf}
              className="flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-slate-600 transition"
              title="Download 1-page CRISIL credit risk alert memorandum"
            >
              <Download className="w-3.5 h-3.5 text-sky-400" />
              <span>{exportingPdf ? 'Compiling PDF...' : 'Export 1-Page Credit Alert (PDF)'}</span>
            </button>

            <button
              onClick={() => {
                onClose()
                if (onNavigateTab) onNavigateTab('rebalance')
              }}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white transition shadow-sm"
            >
              <span>Test Rebalance in Module A</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>

            <button
              onClick={() => {
                onClose()
                if (onNavigateTab) onNavigateTab('stress')
              }}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold bg-purple-600 hover:bg-purple-500 text-white transition shadow-sm"
            >
              <span>Simulate in Module B</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
