import React from 'react'
import { Activity, RefreshCw, ShieldCheck } from 'lucide-react'

export default function Navbar({ isConnected, onRefresh, loading }) {
  return (
    <header className="border-b border-slate-800 bg-[#0b101b]/80 backdrop-blur-md sticky top-0 z-50 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
                RiskPulse <span className="text-sky-400">AI</span>
              </h1>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300 font-mono">
                v1.0.0
              </span>
            </div>
            <p className="text-xs text-slate-400">
              S&P Global × CRISIL Campus Hackathon 2026 • Candidate: <span className="text-slate-200 font-medium">Arpit Gupta (VIT Bhopal)</span>
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
            <span className="text-slate-300">
              {isConnected ? 'FastAPI Risk Bus Online' : 'Connecting to Engine...'}
            </span>
          </div>

          <button
            onClick={onRefresh}
            disabled={loading}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-sky-600/20 hover:bg-sky-600/30 border border-sky-500/30 text-sky-300 text-xs font-medium transition duration-150 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Reload Feeds</span>
          </button>
        </div>
      </div>
    </header>
  )
}
