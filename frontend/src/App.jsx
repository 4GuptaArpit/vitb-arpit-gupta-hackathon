import React, { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import KpiBar from './components/KpiBar'
import SignalFeedTab from './components/SignalFeedTab'
import RebalanceTab from './components/RebalanceTab'
import StressTestTab from './components/StressTestTab'
import AdhocTab from './components/AdhocTab'
import { fetchHealth, fetchSignals } from './api'
import { Radio, BarChart3, Landmark, Sparkles } from 'lucide-react'

export default function App() {
  const [signals, setSignals] = useState([])
  const [activeTab, setActiveTab] = useState('feed')
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
        {/* Navigation Tabs */}
        <div className="flex space-x-2 border-b border-slate-800 pb-2 overflow-x-auto">
          {tabs.map(t => {
            const Icon = t.icon
            const active = activeTab === t.id
            return (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
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

        {/* Tab Content Panels */}
        <div className="pt-2">
          {activeTab === 'feed' && <SignalFeedTab signals={signals} />}
          {activeTab === 'rebalance' && <RebalanceTab />}
          {activeTab === 'stress' && <StressTestTab />}
          {activeTab === 'adhoc' && <AdhocTab />}
        </div>
      </main>

      <footer className="border-t border-slate-800/80 bg-[#0b101b] py-4 text-center text-xs text-slate-500">
        RiskPulse AI • Built for S&P Global × CRISIL Campus Hackathon 2026 • Vellore Institute of Technology, Bhopal
      </footer>
    </div>
  )
}
