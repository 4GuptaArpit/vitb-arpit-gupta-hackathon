import React, { useState } from 'react'
import { Sparkles, Terminal, Tag, CheckCircle } from 'lucide-react'
import { analyzeAdhocText } from '../api'

export default function AdhocTab() {
  const [text, setText] = useState("Moody's places senior unsecured notes on downgrade review due to ballooning debt maturities and liquidity crunch.")
  const [ticker, setTicker] = useState("XYZ")
  const [engagement, setEngagement] = useState(150)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleAnalyze() {
    if (!text.trim()) return
    setLoading(true)
    try {
      const data = await analyzeAdhocText(text, ticker, engagement)
      setResult(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-[#0f172a]/70 p-5 rounded-xl border border-slate-800 space-y-4">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-sky-400" />
          Live Ad-Hoc NLP Signal Analysis
        </h3>
        <p className="text-xs text-slate-400">
          Paste any live headline, earnings report snippet, or regulatory notice to test real-time FinBERT risk scoring.
        </p>

        <textarea
          rows={3}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter financial news text here..."
          className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
        />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label className="text-xs text-slate-400 block mb-1">Company Ticker (optional)</label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white uppercase focus:outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Market Engagement / Virality:</span>
              <span className="font-mono text-sky-400 font-bold">{engagement}</span>
            </div>
            <input
              type="range"
              min="0"
              max="500"
              value={engagement}
              onChange={(e) => setEngagement(Number(e.target.value))}
              className="w-full accent-sky-500 cursor-pointer"
            />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold text-xs transition duration-150 disabled:opacity-50"
          >
            {loading ? 'Analyzing Sentiment...' : 'Score Risk Signal Live'}
          </button>
        </div>
      </div>

      {result && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-[#0f172a]/70 p-4 rounded-xl border border-slate-800">
            <span className="text-xs text-slate-400">Calibrated Sentiment</span>
            <div className="flex items-baseline space-x-2 mt-1">
              <span className={`text-2xl font-bold font-mono ${result.sentiment_score >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {result.sentiment_score > 0 ? `+${result.sentiment_score.toFixed(2)}` : result.sentiment_score.toFixed(2)}
              </span>
              <span className="text-xs text-slate-400">({result.sentiment_label})</span>
            </div>
          </div>

          <div className="bg-[#0f172a]/70 p-4 rounded-xl border border-slate-800">
            <span className="text-xs text-slate-400">Event Classification</span>
            <div className="flex items-baseline space-x-2 mt-1">
              <span className="text-lg font-bold text-white">{result.event_classification}</span>
              <span className="text-xs text-sky-400 font-mono">{(result.confidence_score * 100).toFixed(0)}% Conf.</span>
            </div>
          </div>

          <div className="bg-[#0f172a]/70 p-4 rounded-xl border border-slate-800">
            <span className="text-xs text-slate-400">Predicted Impact Severity</span>
            <div className="flex items-baseline space-x-2 mt-1">
              <span className={`text-2xl font-bold font-mono ${result.impact_score >= 7 ? 'text-rose-400' : 'text-amber-400'}`}>
                {result.impact_score} / 10
              </span>
              <span className="text-xs text-slate-400">
                {result.impact_score >= 7 ? 'Elevated Market Risk' : 'Moderate Severity'}
              </span>
            </div>
          </div>

          <div className="col-span-1 md:col-span-3 bg-[#0f172a]/70 p-4 rounded-xl border border-slate-800">
            <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300 mb-2">
              <Terminal className="w-3.5 h-3.5 text-sky-400" />
              <span>Structured RiskSignal JSON Payload</span>
            </div>
            <pre className="bg-slate-950 p-3 rounded-lg font-mono text-[11px] text-sky-300 overflow-x-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}
