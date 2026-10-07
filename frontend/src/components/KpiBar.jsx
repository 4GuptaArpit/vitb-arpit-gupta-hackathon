import React from 'react'
import { TrendingUp, TrendingDown, AlertTriangle, Layers, Zap } from 'lucide-react'

export default function KpiBar({ signals }) {
  const total = signals.length
  const avgSentiment = total > 0 ? (signals.reduce((acc, s) => acc + s.sentiment_score, 0) / total).toFixed(2) : '0.00'
  const highImpact = signals.filter(s => s.impact_score >= 7).length
  const positive = signals.filter(s => s.sentiment_score > 0.15).length
  const negative = signals.filter(s => s.sentiment_score < -0.15).length

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 max-w-7xl mx-auto px-6 pt-5 pb-2">
      <div className="bg-[#0f172a]/70 border border-slate-800/80 rounded-xl p-3.5 backdrop-blur-sm">
        <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
          <span>Ingested Streams</span>
          <Layers className="w-3.5 h-3.5 text-sky-400" />
        </div>
        <div className="text-xl font-bold font-mono-numbers text-white">{total} Feeds</div>
        <div className="text-[11px] text-slate-500 mt-0.5">News & Social Ingestion</div>
      </div>

      <div className="bg-[#0f172a]/70 border border-slate-800/80 rounded-xl p-3.5 backdrop-blur-sm">
        <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
          <span>Mean Market Sentiment</span>
          <Zap className="w-3.5 h-3.5 text-amber-400" />
        </div>
        <div className={`text-xl font-bold font-mono-numbers ${Number(avgSentiment) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
          {Number(avgSentiment) > 0 ? `+${avgSentiment}` : avgSentiment}
        </div>
        <div className="text-[11px] text-slate-500 mt-0.5">Scale: -1.0 to +1.0</div>
      </div>

      <div className="bg-[#0f172a]/70 border border-slate-800/80 rounded-xl p-3.5 backdrop-blur-sm">
        <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
          <span>High Severity Alerts</span>
          <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
        </div>
        <div className="text-xl font-bold font-mono-numbers text-rose-400">{highImpact}</div>
        <div className="text-[11px] text-rose-500/80 mt-0.5">Impact Score ≥ 7 / 10</div>
      </div>

      <div className="bg-[#0f172a]/70 border border-slate-800/80 rounded-xl p-3.5 backdrop-blur-sm">
        <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
          <span>Bullish Signals</span>
          <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
        </div>
        <div className="text-xl font-bold font-mono-numbers text-emerald-400">{positive}</div>
        <div className="text-[11px] text-emerald-500/80 mt-0.5">Score &gt; +0.15</div>
      </div>

      <div className="bg-[#0f172a]/70 border border-slate-800/80 rounded-xl p-3.5 backdrop-blur-sm col-span-2 md:col-span-1">
        <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
          <span>Bearish Signals</span>
          <TrendingDown className="w-3.5 h-3.5 text-rose-400" />
        </div>
        <div className="text-xl font-bold font-mono-numbers text-rose-400">{negative}</div>
        <div className="text-[11px] text-rose-500/80 mt-0.5">Score &lt; -0.15</div>
      </div>
    </div>
  )
}
