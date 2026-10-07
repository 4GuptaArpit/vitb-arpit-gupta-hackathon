import React, { useState } from 'react'
import { Filter, Search, Tag, ExternalLink } from 'lucide-react'

export default function SignalFeedTab({ signals }) {
  const [selectedEvent, setSelectedEvent] = useState('All')
  const [searchTerm, setSearchTerm] = useState('')
  const [minImpact, setMinImpact] = useState(1)

  const events = ['All', 'Geopolitical', 'Credit Event', 'Macroeconomic', 'Regulatory', 'Merger/Acquisition', 'Product Launch']

  const filtered = signals.filter(s => {
    const matchesEvent = selectedEvent === 'All' || s.event_classification === selectedEvent
    const matchesImpact = s.impact_score >= minImpact
    const matchesSearch = searchTerm === '' ||
      s.ticker.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.headline.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesEvent && matchesImpact && matchesSearch
  })

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-[#0f172a]/70 p-4 rounded-xl border border-slate-800">
        <div className="flex items-center space-x-2 flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search company ticker (e.g. AAPL, NVDA) or headline..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1.5">
            <span className="text-slate-400">Category:</span>
            <select
              value={selectedEvent}
              onChange={(e) => setSelectedEvent(e.target.value)}
              className="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-sky-500"
            >
              {events.map(ev => <option key={ev} value={ev}>{ev}</option>)}
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-slate-400">Min Impact:</span>
            <input
              type="range"
              min="1"
              max="10"
              value={minImpact}
              onChange={(e) => setMinImpact(Number(e.target.value))}
              className="w-20 accent-sky-500 cursor-pointer"
            />
            <span className="font-mono text-sky-400 font-semibold">{minImpact}</span>
          </div>
        </div>
      </div>

      {/* Signal Stream Cards */}
      <div className="space-y-2.5 max-h-[640px] overflow-y-auto pr-1">
        {filtered.map((sig) => (
          <div
            key={sig.id}
            className="p-3.5 bg-[#0f172a]/60 hover:bg-[#131c33] border border-slate-800 hover:border-slate-700 rounded-xl transition duration-150"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center space-x-2.5">
                <span className="font-mono text-sm font-bold px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-sky-400">
                  {sig.ticker}
                </span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800/80 text-slate-300 font-medium">
                  {sig.event_classification}
                </span>
                <span className="text-xs text-slate-500 font-mono">
                  {sig.publisher}
                </span>
              </div>

              <div className="flex items-center space-x-2">
                <span className={`text-xs px-2.5 py-0.5 rounded font-mono font-semibold ${
                  sig.sentiment_score > 0.15
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : sig.sentiment_score < -0.15
                    ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                    : 'bg-slate-800 text-slate-300'
                }`}>
                  {sig.sentiment_score > 0 ? `+${sig.sentiment_score.toFixed(2)}` : sig.sentiment_score.toFixed(2)}
                </span>
                <span className={`text-xs px-2 py-0.5 rounded font-mono font-bold ${
                  sig.impact_score >= 7 ? 'bg-rose-500/20 text-rose-300' : 'bg-slate-800 text-slate-400'
                }`}>
                  Impact {sig.impact_score}/10
                </span>
              </div>
            </div>

            <p className="text-xs text-slate-200 font-medium mt-2 leading-relaxed">
              {sig.headline}
            </p>

            {sig.key_drivers && sig.key_drivers.length > 0 && (
              <div className="flex items-center space-x-1.5 mt-2.5 text-[11px] text-slate-400">
                <Tag className="w-3 h-3 text-sky-400" />
                <span className="text-slate-500">Key NLP Drivers:</span>
                <span className="text-slate-300 font-mono">{sig.key_drivers.join(', ')}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
