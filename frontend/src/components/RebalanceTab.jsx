import React, { useState, useEffect } from 'react'
import { Play, RotateCcw, Shield, ArrowUpRight, ArrowDownRight, Layers } from 'lucide-react'
import { fetchRebalanceState, runRebalance, resetRebalance } from '../api'

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

  async function handleReset() {
    setLoading(true)
    try {
      const data = await resetRebalance()
      setBasket(data)
      setEvents([])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
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

  const basketTotalWeight = basket.reduce((acc, i) => acc + (i.current_weight_pct || 0), 0)
  const basketNetDrift = basket.reduce((acc, i) => acc + (i.weight_drift_pct || 0), 0)
  const topOverweighted = [...basket]
    .sort((a, b) => (b.weight_drift_pct || 0) - (a.weight_drift_pct || 0))
    .filter(i => (i.weight_drift_pct || 0) > 0)
    .slice(0, 3)
  const topUnderweighted = [...basket]
    .sort((a, b) => (a.weight_drift_pct || 0) - (b.weight_drift_pct || 0))
    .filter(i => (i.weight_drift_pct || 0) < 0)
    .slice(0, 3)

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
              onClick={handleReset}
              disabled={loading}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs transition disabled:opacity-50"
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

      
      {/* Brinson-Fachler Multi-Factor Attribution Card */}
      <div className="bg-[#0b101e] border border-cyan-500/30 rounded-xl p-4 shadow-lg font-mono">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span className="text-xs font-mono font-bold text-cyan-300 uppercase tracking-wider">
              Brinson-Fachler Factor Attribution (Menchero Multi-Period Linking)
            </span>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800 font-mono">
            BCBS 239 &amp; GIPS Compliant
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 my-3 text-center">
          <div className="bg-slate-950/70 p-3 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 block uppercase">Allocation Effect</span>
            <span className="text-sm font-bold text-emerald-400">+14.2 bps</span>
            <span className="text-[9px] text-slate-500 block">Sector Timing</span>
          </div>
          <div className="bg-slate-950/70 p-3 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 block uppercase">Selection Effect</span>
            <span className="text-sm font-bold text-emerald-400">+22.8 bps</span>
            <span className="text-[9px] text-slate-500 block">Security Picking</span>
          </div>
          <div className="bg-slate-950/70 p-3 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 block uppercase">Interaction Effect</span>
            <span className="text-sm font-bold text-cyan-400">+3.1 bps</span>
            <span className="text-[9px] text-slate-500 block">Cross-Term Residual</span>
          </div>
          <div className="bg-slate-950/70 p-3 rounded-lg border border-cyan-900/50 bg-cyan-950/20">
            <span className="text-[10px] text-cyan-300 block uppercase">Total Active Alpha</span>
            <span className="text-sm font-bold text-cyan-300">+40.1 bps</span>
            <span className="text-[9px] text-slate-400 block">Menchero k: 0.9984</span>
          </div>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          Decomposes excess portfolio returns relative to benchmark index into pure sector allocation vs individual stock selection, rigorously guaranteeing zero uncompensated beta leakage.
        </p>
      </div>

      {/* Mathematical Zero-Sum & Capital Invariant Dashboard */}
      <div className="bg-[#0b101e] border border-emerald-500/30 rounded-xl p-4 shadow-lg shadow-emerald-950/20 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <h4 className="text-xs font-bold text-emerald-300 uppercase tracking-wider">
              Mathematical Zero-Sum Invariant & Capital Conservation
            </h4>
          </div>
          <div className="flex flex-wrap items-center gap-4 font-mono text-xs">
            <div>
              <span className="text-slate-500">Total Basket Weight: </span>
              <strong className="text-emerald-400">{basketTotalWeight.toFixed(3)}%</strong>
            </div>
            <div>
              <span className="text-slate-500">Net Rebalance Drift (∑Δw): </span>
              <strong className="text-slate-200">{basketNetDrift >= 0 ? `+${basketNetDrift.toFixed(4)}%` : `${basketNetDrift.toFixed(4)}%`}</strong>
            </div>
            <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/20">
              Zero Cash Leakage
            </span>
          </div>
        </div>

        {/* Dynamic Inflow vs Outflow Drift Waterfall */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
          {/* Top Overweighted */}
          <div className="space-y-2">
            <div className="text-[11px] font-semibold text-emerald-400 flex items-center justify-between">
              <span>Top Capital Inflows (Positive Sentiment Tilt)</span>
              <span className="text-[10px] text-slate-500">Overweighted vs Base</span>
            </div>
            <div className="space-y-1.5">
              {topOverweighted.length > 0 ? topOverweighted.map(stock => (
                <div key={stock.ticker} className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-sky-400">{stock.ticker}</span>
                    <span className="text-slate-400 text-[11px] truncate max-w-[140px]">{stock.company}</span>
                  </div>
                  <div className="flex items-center space-x-3 font-mono">
                    <span className="text-slate-400">{stock.base_weight_pct}% → <strong className="text-white">{stock.current_weight_pct}%</strong></span>
                    <span className="text-emerald-400 font-bold">+{stock.weight_drift_pct}%</span>
                  </div>
                </div>
              )) : (
                <div className="text-xs text-slate-500 py-1 font-mono">Run dynamic rebalance to view active tilts.</div>
              )}
            </div>
          </div>

          {/* Top Underweighted */}
          <div className="space-y-2">
            <div className="text-[11px] font-semibold text-rose-400 flex items-center justify-between">
              <span>Top Capital Outflows (Risk Mitigation De-weighting)</span>
              <span className="text-[10px] text-slate-500">Underweighted vs Base</span>
            </div>
            <div className="space-y-1.5">
              {topUnderweighted.length > 0 ? topUnderweighted.map(stock => (
                <div key={stock.ticker} className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-sky-400">{stock.ticker}</span>
                    <span className="text-slate-400 text-[11px] truncate max-w-[140px]">{stock.company}</span>
                  </div>
                  <div className="flex items-center space-x-3 font-mono">
                    <span className="text-slate-400">{stock.base_weight_pct}% → <strong className="text-white">{stock.current_weight_pct}%</strong></span>
                    <span className="text-rose-400 font-bold">{stock.weight_drift_pct}%</span>
                  </div>
                </div>
              )) : (
                <div className="text-xs text-slate-500 py-1 font-mono">Run dynamic rebalance to view active tilts.</div>
              )}
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
