import React, { useState, useEffect } from 'react'
import { Play, RotateCcw, Shield, ArrowUpRight, ArrowDownRight, Layers } from 'lucide-react'
import { fetchRebalanceState, runRebalance } from '../api'

export default function RebalanceTab() {
  const [basket, setBasket] = useState([])
  const [events, setEvents] = useState([])
  const [alpha, setAlpha] = useState(0.35)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadState()
  }, [])

  async function loadState() {
    try {
      const data = await fetchRebalanceState()
      setBasket(data)
    } catch (e) {
      console.error(e)
    }
  }

  async function handleRebalance() {
    setLoading(true)
    try {
      const res = await runRebalance(alpha)
      setBasket(res.state)
      setEvents(res.recent_events)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Controls & Parameters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-[#0f172a]/70 p-5 rounded-xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Layers className="w-4 h-4 text-sky-400" />
            Execution Parameters
          </h3>

          <div>
            <div className="flex justify-between text-xs text-slate-300 mb-1.5">
              <span>Sensitivity Alpha (α):</span>
              <span className="font-mono text-sky-400 font-bold">{alpha}</span>
            </div>
            <input
              type="range"
              min="0.10"
              max="0.80"
              step="0.05"
              value={alpha}
              onChange={(e) => setAlpha(parseFloat(e.target.value))}
              className="w-full accent-sky-500 cursor-pointer"
            />
            <p className="text-[11px] text-slate-500 mt-1">
              Scales sentiment magnitude into target weight adjustments.
            </p>
          </div>

          <div className="pt-2 flex flex-col gap-2">
            <button
              onClick={handleRebalance}
              disabled={loading}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold text-xs transition duration-150 shadow-lg shadow-sky-500/20 disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{loading ? 'Rebalancing...' : 'Run Dynamic Rebalance'}</span>
            </button>

            <button
              onClick={loadState}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs transition"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Reset to Benchmark</span>
            </button>
          </div>
        </div>

        {/* Institutional Guardrails Box */}
        <div className="bg-[#0f172a]/70 p-5 rounded-xl border border-slate-800 space-y-3 col-span-1 md:col-span-2">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-400" />
            Institutional Portfolio Guardrails
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <span className="text-[11px] text-slate-400">Sum of Weights</span>
              <p className="text-base font-bold font-mono text-emerald-400 mt-0.5">Strictly 100.0%</p>
              <p className="text-[10px] text-slate-500 mt-1">Continuous normalization</p>
            </div>
            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <span className="text-[11px] text-slate-400">Diversification Floor</span>
              <p className="text-base font-bold font-mono text-sky-400 mt-0.5">1.0% Min</p>
              <p className="text-[10px] text-slate-500 mt-1">Guarantees basket breadth</p>
            </div>
            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <span className="text-[11px] text-slate-400">Concentration Cap</span>
              <p className="text-base font-bold font-mono text-amber-400 mt-0.5">18.0% Max</p>
              <p className="text-[10px] text-slate-500 mt-1">Prevents single-asset blowout</p>
            </div>
          </div>
        </div>
      </div>

      {/* S&P 100 Constituent Basket Grid */}
      <div>
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
          S&P 100 Constituent Weights & Sentiment Drift
        </h4>
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 gap-3">
          {basket.map((item) => (
            <div
              key={item.ticker}
              className="bg-[#0f172a]/70 hover:bg-[#131c33] border border-slate-800 p-3.5 rounded-xl transition duration-150"
            >
              <div className="flex justify-between items-start">
                <span className="font-mono text-sm font-bold text-sky-400">{item.ticker}</span>
                <span className={`text-[11px] font-mono flex items-center ${
                  item.weight_drift_pct > 0 ? 'text-emerald-400 font-semibold' : item.weight_drift_pct < 0 ? 'text-rose-400 font-semibold' : 'text-slate-400'
                }`}>
                  {item.weight_drift_pct > 0 && <ArrowUpRight className="w-3 h-3" />}
                  {item.weight_drift_pct < 0 && <ArrowDownRight className="w-3 h-3" />}
                  {item.weight_drift_pct > 0 ? `+${item.weight_drift_pct}%` : `${item.weight_drift_pct}%`}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 truncate mt-1">{item.company}</p>
              <div className="mt-2.5 flex items-baseline justify-between">
                <span className="text-lg font-bold font-mono text-white">{item.current_weight_pct}%</span>
                <span className="text-[10px] text-slate-500">Base: {item.base_weight_pct}%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-1 mt-2 overflow-hidden">
                <div
                  className="bg-sky-400 h-1 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(100, item.current_weight_pct * 5)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Rebalance Audit Log */}
      {events && events.length > 0 && (
        <div className="bg-[#0f172a]/70 p-4 rounded-xl border border-slate-800">
          <h4 className="text-xs font-semibold text-slate-300 mb-3">Recent Execution Logs</h4>
          <div className="space-y-1.5 max-h-48 overflow-y-auto font-mono text-xs text-slate-400">
            {events.map((ev, idx) => (
              <div key={idx} className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-sky-400 font-semibold">{ev.ticker_affected}</span>
                <span>{ev.summary}</span>
                <span className="text-slate-500">{ev.timestamp}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
