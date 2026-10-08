/**
 * API client communicating with FastAPI backend (port 8000).
 */

const API_BASE = window.location.port === '5173' ? 'http://127.0.0.1:8000' : ''

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`)
  return res.json()
}

export async function fetchSignals(limit = 100, eventType = null, minImpact = null) {
  let url = `${API_BASE}/signals?limit=${limit}`
  if (eventType && eventType !== 'All') url += `&event_type=${encodeURIComponent(eventType)}`
  if (minImpact && minImpact > 1) url += `&min_impact=${minImpact}`
  const res = await fetch(url)
  return res.json()
}

export async function fetchRebalanceState() {
  const res = await fetch(`${API_BASE}/api/rebalance/state`)
  return res.json()
}

export async function runRebalance(sensitivityAlpha = 0.35) {
  const res = await fetch(`${API_BASE}/api/rebalance/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sensitivity_alpha: sensitivityAlpha })
  })
  return res.json()
}

export async function resetRebalance() {
  const res = await fetch(`${API_BASE}/api/rebalance/reset`, {
    method: 'POST'
  })
  return res.json()
}


export async function runStressTest(eventType, impactScore, targetSector = null) {
  const res = await fetch(`${API_BASE}/api/stress-test/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      event_type: eventType,
      impact_score: impactScore,
      target_sector: targetSector
    })
  })
  return res.json()
}

export async function analyzeAdhocText(text, ticker = 'GENERAL', engagement = 100) {
  const res = await fetch(`${API_BASE}/signals/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text,
      ticker: ticker || 'GENERAL',
      engagement: Number(engagement) || 0
    })
  })
  return res.json()
}
