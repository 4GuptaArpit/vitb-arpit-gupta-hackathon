import CommandBar from './components/CommandBar';
import React, { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import KpiBar from './components/KpiBar'
import SignalFeedTab from './components/SignalFeedTab'
import RebalanceTab from './components/RebalanceTab'
import StressTestTab from './components/StressTestTab'
import AdhocTab from './components/AdhocTab'
import { fetchHealth, fetchSignals } from './api'
import { Radio, BarChart3, Landmark, Sparkles, LayoutGrid, Columns } from 'lucide-react'

export default function App() {
  const [signals, setSignals] = useState([])
  const [activeTab, setActiveTab] = useState('feed')
  const [viewMode, setViewMode] = useState('tabs') // 'tabs' | 'quadrant'
  const [isConnected, setIsConnected] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    checkHealthAndLoad()
  }, [])

  async function checkHealthAndLoad() {
    setLoading(true)
    try {
      await fetchHealth()
      setIsConnected(true)
      const data = await fetchSignals(100)
      setSignals(data)
    } catch (e) {
      console.warn("Backend not reached yet:", e)
      setIsConnected(false)
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { id: 'feed', label: 'NLP Risk Signals', icon: Radio },
    { id: 'rebalance', label: 'Module A: Tactical Rebalancer', icon: BarChart3 },
    { id: 'stress', label: 'Module B: Wholesale Stress Tester', icon: Landmark },
    { id: 'adhoc', label: 'Ad-Hoc Live Tester', icon: Sparkles },
  ]

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 flex flex-col font-sans">
      <Navbar isConnected={isConnected} onRefresh={checkHealthAndLoad} loading={loading} />
      <KpiBar signals={signals} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-4 space-y-6">
        {/* Navigation Bar with View Mode Switcher */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-2">
          {/* Tabs */}
          <div className="flex space-x-2 overflow-x-auto">
            {tabs.map(t => {
              const Icon = t.icon
              const active = activeTab === t.id && viewMode === 'tabs'
              return (
                <button
                  key={t.id}
                  onClick={() => {
                    setActiveTab(t.id)
                    setViewMode('tabs')
                  }}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition duration-150 whitespace-nowrap ${
                    active
                      ? 'bg-sky-500/10 text-sky-400 border border-sky-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{t.label}</span>
                </button>
              )
            })}
          </div>

          {/* View Mode Switcher */}
          <div className="flex items-center space-x-1 p-1 bg-slate-900/90 border border-slate-800 rounded-lg text-xs font-mono">
            <button
              onClick={() => setViewMode('tabs')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md transition ${
                viewMode === 'tabs'
                  ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Columns className="w-3.5 h-3.5" />
              <span>Focused View</span>
            </button>
            <button
              onClick={() => setViewMode('quadrant')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md transition ${
                viewMode === 'quadrant'
                  ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30 font-bold shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <LayoutGrid className="w-3.5 h-3.5 text-sky-400" />
              <span>4-Quadrant Command Desk</span>
            </button>
          </div>
        </div>

        {/* Viewport Panels */}
        {viewMode === 'tabs' ? (
          <div className="pt-2">
            {activeTab === 'feed' && <SignalFeedTab signals={signals} onNavigateTab={setActiveTab} />}
            {activeTab === 'rebalance' && <RebalanceTab />}
            {activeTab === 'stress' && <StressTestTab />}
            {activeTab === 'adhoc' && <AdhocTab />}
          </div>
        ) : (
          /* 4-Quadrant Command Desk Mode */
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 pt-2">
            {/* Window 1: Live Signals */}
            <div className="bg-[#0b101e]/90 border border-slate-800 rounded-xl p-4 flex flex-col space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 rounded-full bg-sky-400 animate-pulse" />
                  <span className="text-xs font-mono font-bold text-sky-400 uppercase tracking-wider">
                    Window 01 // Live Signal Bus Telemetry
                  </span>
                </div>
                <button
                  onClick={() => { setActiveTab('feed'); setViewMode('tabs'); }}
                  className="text-[11px] text-slate-500 hover:text-sky-300 font-mono underline"
                >
                  Maximize
                </button>
              </div>
              <div className="overflow-y-auto max-h-[500px]">
                <SignalFeedTab signals={signals} onNavigateTab={setActiveTab} />
              </div>
            </div>

            {/* Window 2: Module A Rebalancer */}
            <div className="bg-[#0b101e]/90 border border-slate-800 rounded-xl p-4 flex flex-col space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400" />
                  <span className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider">
                    Window 02 // Module A: Tactical Rebalancer
                  </span>
                </div>
                <button
                  onClick={() => { setActiveTab('rebalance'); setViewMode('tabs'); }}
                  className="text-[11px] text-slate-500 hover:text-emerald-300 font-mono underline"
                >
                  Maximize
                </button>
              </div>
              <div className="overflow-y-auto max-h-[500px]">
                <RebalanceTab />
              </div>
            </div>

            {/* Window 3: Module B Stress Tester */}
            <div className="bg-[#0b101e]/90 border border-slate-800 rounded-xl p-4 flex flex-col space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 rounded-full bg-purple-400" />
                  <span className="text-xs font-mono font-bold text-purple-400 uppercase tracking-wider">
                    Window 03 // Module B: Wholesale Credit Stress
                  </span>
                </div>
                <button
                  onClick={() => { setActiveTab('stress'); setViewMode('tabs'); }}
                  className="text-[11px] text-slate-500 hover:text-purple-300 font-mono underline"
                >
                  Maximize
                </button>
              </div>
              <div className="overflow-y-auto max-h-[500px]">
                <StressTestTab />
              </div>
            </div>

            {/* Window 4: Ad-Hoc Sandbox */}
            <div className="bg-[#0b101e]/90 border border-slate-800 rounded-xl p-4 flex flex-col space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 rounded-full bg-amber-400" />
                  <span className="text-xs font-mono font-bold text-amber-400 uppercase tracking-wider">
                    Window 04 // Ad-Hoc NLP Risk Scoring Sandbox
                  </span>
                </div>
                <button
                  onClick={() => { setActiveTab('adhoc'); setViewMode('tabs'); }}
                  className="text-[11px] text-slate-500 hover:text-amber-300 font-mono underline"
                >
                  Maximize
                </button>
              </div>
              <div className="overflow-y-auto max-h-[500px]">
                <AdhocTab />
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="border-t border-slate-800/80 bg-[#0b101b] py-4 text-center text-xs text-slate-500">
        RiskPulse AI • Built for S&P Global × CRISIL Campus Hackathon 2026 • Vellore Institute of Technology, Bhopal
      </footer>
    </div>
  )
}
