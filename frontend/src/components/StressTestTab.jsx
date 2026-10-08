import React, { useState, useEffect } from 'react'
import { Flame, DollarSign, TrendingDown, AlertOctagon, FileDown } from 'lucide-react'
import { runStressTest } from '../api'

export default function StressTestTab() {
  const [eventType, setEventType] = useState('Geopolitical')
  const [impactScore, setImpactScore] = useState(8)
  const [targetSector, setTargetSector] = useState('None')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [exportingPdf, setExportingPdf] = useState(false)

  async function handleExportStressPdf() {
    try {
      setExportingPdf(true)
      const res = await fetch(`/api/reports/stress-test/export?event_type=${encodeURIComponent(eventType)}&impact_score=${impactScore}&shock_multiplier=1.0`, {
        method: 'POST'
      })
      if (!res.ok) throw new Error('Failed to generate Stress PDF')
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `CRISIL_Stress_Report_${eventType.replace(/\s+/g, '_')}_Sev${impactScore}.pdf`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (e) {
      console.error(e)
      alert('Could not export Stress Report PDF.')
    } finally {
      setExportingPdf(false)
    }
  }

  const events = ['Geopolitical', 'Credit Event', 'Macroeconomic', 'Regulatory', 'Merger/Acquisition', 'Product Launch']
  const sectors = ['None', 'Energy', 'Financial Services', 'Semiconductors', 'Telecommunications', 'Automotive', 'Healthcare']

  useEffect(() => {
    executeSimulation()
  }, [])

  async function executeSimulation() {
    setLoading(true)
    try {
      const data = await runStressTest(eventType, impactScore, targetSector === 'None' ? null : targetSector)
      setResult(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Simulation Controls */}
      <div className="bg-[#0f172a]/70 p-5 rounded-xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Flame className="w-4 h-4 text-rose-400" />
            Strategic Shock Scenario Generator
          </h3>
          <span className="text-xs font-mono text-slate-400">Target: $1.10B Wholesale Book</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-slate-400 block mb-1.5">Trigger Event Type</label>
            <select
              value={eventType}
              onChange={(e) => setEventType(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-xs text-slate-200 focus:outline-none focus:border-rose-500"
            >
              {events.map(ev => <option key={ev} value={ev}>{ev}</option>)}
            </select>
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-400 mb-1.5">
              <span>Event Severity (1-10):</span>
              <span className="font-mono text-rose-400 font-bold">{impactScore}</span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              value={impactScore}
              onChange={(e) => setImpactScore(parseInt(e.target.value))}
              className="w-full accent-rose-500 cursor-pointer"
            />
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1.5">Target Sector Vulnerability</label>
            <select
              value={targetSector}
              onChange={(e) => setTargetSector(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-xs text-slate-200 focus:outline-none focus:border-rose-500"
            >
              {sectors.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={executeSimulation}
            disabled={loading}
            className="px-5 py-2 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/30 text-rose-300 text-xs font-semibold transition"
          >
            {loading ? 'Simulating Shocks...' : 'Execute Stress Simulation'}
          </button>

          <button
            onClick={handleExportStressPdf}
            disabled={exportingPdf}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-cyan-950/60 hover:bg-cyan-900/60 border border-cyan-500/40 text-cyan-300 text-xs font-semibold font-mono transition"
            title="Download Institutional C-Suite Stress Memorandum (PDF)"
          >
            <FileDown className={`w-3.5 h-3.5 ${exportingPdf ? 'animate-bounce' : ''}`} />
            <span>{exportingPdf ? 'Compiling PDF...' : 'Export Stress Report PDF'}</span>
          </button>
        </div>
      </div>

      {/* KPI Ribbon */}
      {result && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-[#0f172a]/70 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400">Pre-Stress Baseline</span>
              <p className="text-xl font-bold font-mono text-white mt-1">
                ${(result.baseline_value_usd / 1e6).toFixed(2)}M
              </p>
            </div>

            <div className="bg-[#0f172a]/70 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400">Post-Stress Mark-to-Market</span>
              <p className="text-xl font-bold font-mono text-rose-400 mt-1">
                ${(result.stressed_value_usd / 1e6).toFixed(2)}M
              </p>
              <span className="text-[11px] font-mono text-rose-500">
                ${(result.total_pnl_usd / 1e6).toFixed(2)}M ({result.pnl_percentage.toFixed(2)}%)
              </span>
            </div>

            <div className="bg-[#0f172a]/70 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400">Expected Loss Surge (EL)</span>
              <p className="text-xl font-bold font-mono text-amber-400 mt-1">
                ${(result.stressed_expected_loss_usd / 1e6).toFixed(2)}M
              </p>
              <span className="text-[11px] font-mono text-amber-500">
                +${(result.el_increase_usd / 1e6).toFixed(2)}M
              </span>
            </div>

            <div className="bg-[#0f172a]/70 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400">99% Value-at-Risk (VaR)</span>
              <p className="text-xl font-bold font-mono text-sky-400 mt-1">
                ${(result.var_99_stressed_usd / 1e6).toFixed(2)}M
              </p>
            </div>
          </div>

          {/* Asset Breakdown Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
            {result.asset_breakdown && result.asset_breakdown.map((item) => (
              <div key={item.asset_type} className="bg-[#0f172a]/60 p-3.5 rounded-xl border border-slate-800">
                <span className="text-xs font-semibold text-slate-300 block">{item.asset_type}</span>
                <span className="text-[11px] text-slate-500">{item.positions_count} Positions</span>
                <div className="mt-2 text-sm font-bold font-mono text-rose-400">
                  ${(item.pnl_usd / 1e6).toFixed(2)}M ({item.pnl_pct.toFixed(2)}%)
                </div>
              </div>
            ))}
          </div>

          {/* Detailed Portfolio Table */}
          {result.positions && (
            <div className="bg-[#0f172a]/70 p-4 rounded-xl border border-slate-800">
              <h4 className="text-xs font-semibold text-slate-300 mb-3">Wholesale Portfolio Positions Exposure</h4>
              <div className="overflow-x-auto max-h-64 font-mono text-xs">
                <table className="w-full text-left">
                  <thead className="text-slate-500 border-b border-slate-800">
                    <tr>
                      <th className="py-2">ID</th>
                      <th>Asset</th>
                      <th>Counterparty</th>
                      <th>Rating</th>
                      <th>Baseline ($)</th>
                      <th>Stressed ($)</th>
                      <th>P&L (%)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/40 text-slate-300">
                    {result.positions.slice(0, 15).map(pos => (
                      <tr key={pos.position_id}>
                        <td className="py-1.5 text-sky-400">{pos.position_id}</td>
                        <td>{pos.asset_type}</td>
                        <td className="text-slate-200">{pos.counterparty}</td>
                        <td>{pos.credit_rating}</td>
                        <td>${(pos.current_mv_usd / 1e6).toFixed(2)}M</td>
                        <td className="text-rose-400">${(pos.stressed_mv_usd / 1e6).toFixed(2)}M</td>
                        <td className="text-rose-500">{pos.pnl_pct.toFixed(2)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
