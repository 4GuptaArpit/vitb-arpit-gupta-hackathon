import React, { useState } from 'react'
import { Filter, Search, Tag, ExternalLink, ChevronRight } from 'lucide-react'
import SignalDetailModal from './SignalDetailModal'

export default function SignalFeedTab({ signals, onNavigateTab }) {
  const [selectedEvent, setSelectedEvent] = useState('All')
  const [searchTerm, setSearchTerm] = useState('')
  const [minImpact, setMinImpact] = useState(1)
  const [selectedSignal, setSelectedSignal] = useState(null)

  const events = ['All', 'Geopolitical', 'Credit Event', 'Macroeconomic', 'Regulatory', 'Merger/Acquisition', 'Product Launch']

  const COMPANY_MAP = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corp.',
    'NVDA': 'NVIDIA Corp.',
    'AMZN': 'Amazon.com Inc.',
    'GOOGL': 'Alphabet Google Inc.',
    'META': 'Meta Platforms Facebook Inc.',
    'TSLA': 'Tesla Inc.',
    'JPM': 'JPMorgan Chase & Co.',
    'V': 'Visa Inc.',
    'XOM': 'Exxon Mobil Corp.',
    'CVX': 'Chevron Corp.',
    'UNH': 'UnitedHealth Group',
    'JNJ': 'Johnson & Johnson',
    'PFE': 'Pfizer Inc.',
    'WMT': 'Walmart Inc.',
    'PG': 'Procter & Gamble Co.',
    'CAT': 'Caterpillar Inc.',
    'BA': 'Boeing Co.',
    'HD': 'Home Depot Inc.',
    'DIS': 'Walt Disney Co.'
  }

  const filtered = signals.filter(s => {
    const matchesEvent = selectedEvent === 'All' || s.event_classification === selectedEvent
    const matchesImpact = s.impact_score >= minImpact
    const term = searchTerm.trim().toLowerCase()
    const company = (COMPANY_MAP[s.ticker] || '').toLowerCase()
    const headline = (s.headline || '').toLowerCase()
    const text = (s.text || '').toLowerCase()
    const ticker = (s.ticker || '').toLowerCase()
    const publisher = (s.publisher || '').toLowerCase()

    const matchesSearch = term === '' ||
      ticker.includes(term) ||
      company.includes(term) ||
      headline.includes(term) ||
      text.includes(term) ||
      publisher.includes(term)

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
            onClick={() => setSelectedSignal(sig)}
            className="group p-3.5 bg-[#0f172a]/60 hover:bg-[#131d38] border border-slate-800 hover:border-sky-500/50 rounded-xl transition duration-150 cursor-pointer relative shadow-sm hover:shadow-md hover:shadow-sky-950/30"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center space-x-2.5">
                <span className="font-mono text-sm font-bold px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-sky-400 group-hover:border-sky-500/40">
                  {sig.ticker}
                </span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800/80 text-slate-300 font-medium">
                  {sig.event_classification}
                </span>
                <span className="text-xs text-slate-500 font-mono">
                  {sig.publisher}
                </span>
                {sig.timestamp && (
                  <span className="text-[10px] text-slate-500 font-mono px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800">
                    {sig.timestamp.includes('T') ? sig.timestamp.slice(11, 16) + ' UTC' : 'Live'}
                  </span>
                )}
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
                <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-sky-400 group-hover:translate-x-0.5 transition" />
              </div>
            </div>

            <p className="text-xs text-slate-200 font-medium mt-2 leading-relaxed group-hover:text-white transition">
              {sig.headline}
            </p>

            <div className="flex items-center justify-between mt-2.5 text-[11px] text-slate-400">
              {sig.key_drivers && sig.key_drivers.length > 0 ? (
                <div className="flex items-center space-x-1.5">
                  <Tag className="w-3 h-3 text-sky-400" />
                  <span className="text-slate-500">Key NLP Drivers:</span>
                  <span className="text-slate-300 font-mono">{sig.key_drivers.join(', ')}</span>
                </div>
              ) : <div />}
              <span className="text-[10px] text-sky-400/80 opacity-0 group-hover:opacity-100 transition flex items-center space-x-1 font-medium">
                <span>Inspect impact dossier & XAI</span>
                <ExternalLink className="w-2.5 h-2.5" />
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Deep-Dive Transmission & Explainability Modal */}
      <SignalDetailModal
        signal={selectedSignal}
        onClose={() => setSelectedSignal(null)}
        onNavigateTab={onNavigateTab}
      />
    </div>
  )
}

