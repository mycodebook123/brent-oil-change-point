import { useEffect, useMemo, useState } from 'react'
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine,
} from 'recharts'
import './App.css'

const API_BASE = 'http://127.0.0.1:5000'

const CATEGORY_COLORS = {
  'Conflict': 'var(--color-conflict)',
  'Geopolitical': 'var(--color-geopolitical)',
  'Market Event': 'var(--color-market)',
  'Economic': 'var(--color-economic)',
  'OPEC Policy': 'var(--color-opec)',
  'Sanctions': 'var(--color-sanctions)',
}

function formatUSD(value) {
  return `$${Number(value).toFixed(2)}`
}

export default function App() {
  const [prices, setPrices] = useState([])
  const [events, setEvents] = useState([])
  const [changePoint, setChangePoint] = useState(null)
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState(null)

  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [activeCategories, setActiveCategories] = useState(new Set(Object.keys(CATEGORY_COLORS)))

  useEffect(() => {
    async function loadAll() {
      try {
        const [pricesRes, eventsRes, cpRes, summaryRes] = await Promise.all([
          fetch(`${API_BASE}/api/prices?granularity=monthly`),
          fetch(`${API_BASE}/api/events`),
          fetch(`${API_BASE}/api/change-points`),
          fetch(`${API_BASE}/api/summary`),
        ])
        if (!pricesRes.ok || !eventsRes.ok || !cpRes.ok || !summaryRes.ok) {
          throw new Error('One or more API requests failed')
        }
        setPrices(await pricesRes.json())
        setEvents(await eventsRes.json())
        setChangePoint(await cpRes.json())
        setSummary(await summaryRes.json())
      } catch (err) {
        setErrorMsg(
          `Could not reach the backend at ${API_BASE}. Make sure the Flask server is running (python app.py in dashboard/backend).`
        )
      } finally {
        setLoading(false)
      }
    }
    loadAll()
  }, [])

  const filteredPrices = useMemo(() => {
    return prices
      .filter((p) => {
        if (startDate && p.Date < startDate) return false
        if (endDate && p.Date > endDate) return false
        return true
      })
      .map((p) => ({ ...p, ts: new Date(p.Date).getTime() }))
  }, [prices, startDate, endDate])

  const tauTs = changePoint ? new Date(changePoint.tau_date).getTime() : null

  const filteredEvents = useMemo(() => {
    return events.filter((e) => {
      if (!activeCategories.has(e.Category)) return false
      if (startDate && e.Date < startDate) return false
      if (endDate && e.Date > endDate) return false
      return true
    })
  }, [events, activeCategories, startDate, endDate])

  function toggleCategory(cat) {
    setActiveCategories((prev) => {
      const next = new Set(prev)
      if (next.has(cat)) next.delete(cat)
      else next.add(cat)
      return next
    })
  }

  if (loading) {
    return <div className="status-screen">Loading dashboard…</div>
  }

  if (errorMsg) {
    return <div className="status-screen status-screen--error">{errorMsg}</div>
  }

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <div className="dashboard__brand">
          <span className="dashboard__eyebrow">Birhan Energies</span>
          <h1>Brent Crude — Change Point Analysis</h1>
          <p className="dashboard__subtitle">
            Daily Brent oil prices, 1987–2022, overlaid with a Bayesian-detected
            structural break and researched geopolitical &amp; market events.
          </p>
        </div>
      </header>

      {summary && (
        <section className="stat-row">
          <div className="stat-card">
            <span className="stat-card__label">Date range</span>
            <span className="stat-card__value stat-card__value--mono">
              {summary.start_date} → {summary.end_date}
            </span>
          </div>
          <div className="stat-card">
            <span className="stat-card__label">Observations</span>
            <span className="stat-card__value stat-card__value--mono">{summary.total_observations.toLocaleString()}</span>
          </div>
          <div className="stat-card">
            <span className="stat-card__label">Price range</span>
            <span className="stat-card__value stat-card__value--mono">
              {formatUSD(summary.min_price)} – {formatUSD(summary.max_price)}
            </span>
          </div>
          <div className="stat-card">
            <span className="stat-card__label">Average price</span>
            <span className="stat-card__value stat-card__value--mono">{formatUSD(summary.avg_price)}</span>
          </div>
          {changePoint && (
            <div className="stat-card stat-card--highlight">
              <span className="stat-card__label">Detected change point</span>
              <span className="stat-card__value stat-card__value--mono">{changePoint.tau_date}</span>
              <span className="stat-card__footnote">
                {(changePoint.prob_increase * 100).toFixed(1)}% posterior probability mean return increased after this date
              </span>
            </div>
          )}
        </section>
      )}

      <section className="filter-bar">
        <div className="filter-bar__dates">
          <label>
            From
            <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} min="1987-05-20" max="2022-11-14" />
          </label>
          <label>
            To
            <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} min="1987-05-20" max="2022-11-14" />
          </label>
          {(startDate || endDate) && (
            <button className="filter-bar__reset" onClick={() => { setStartDate(''); setEndDate('') }}>
              Reset dates
            </button>
          )}
        </div>
        <div className="filter-bar__categories">
          {Object.entries(CATEGORY_COLORS).map(([cat, color]) => (
            <button
              key={cat}
              className={`chip ${activeCategories.has(cat) ? 'chip--active' : ''}`}
              style={{ '--chip-color': color }}
              onClick={() => toggleCategory(cat)}
            >
              <span className="chip__dot" />
              {cat}
            </button>
          ))}
        </div>
      </section>

      <section className="chart-panel">
        <h2>Monthly average price (USD/barrel)</h2>
        <ResponsiveContainer width="100%" height={420}>
          <LineChart data={filteredPrices} margin={{ top: 10, right: 24, bottom: 10, left: 0 }}>
            <CartesianGrid stroke="var(--color-border)" strokeDasharray="3 3" />
            <XAxis
              dataKey="ts"
              type="number"
              scale="time"
              domain={['dataMin', 'dataMax']}
              tickFormatter={(ts) => new Date(ts).toISOString().slice(0, 7)}
              tick={{ fontFamily: 'var(--font-mono)', fontSize: 11, fill: 'var(--color-ink-muted)' }}
              minTickGap={60}
            />
            <YAxis
              tick={{ fontFamily: 'var(--font-mono)', fontSize: 11, fill: 'var(--color-ink-muted)' }}
              tickFormatter={(v) => `$${v}`}
              width={56}
            />
            <Tooltip
              formatter={(value) => [formatUSD(value), 'Price']}
              contentStyle={{ fontFamily: 'var(--font-mono)', fontSize: 12, borderRadius: 6, border: '1px solid var(--color-border)' }}
            />
            <Line type="monotone" dataKey="Price" stroke="var(--color-primary)" strokeWidth={1.75} dot={false} />
            {tauTs && (
              <ReferenceLine
                x={tauTs}
                stroke="var(--color-changepoint)"
                strokeWidth={2}
                strokeDasharray="6 4"
                label={{ value: 'Change point', position: 'insideTopRight', fill: 'var(--color-changepoint)', fontFamily: 'var(--font-mono)', fontSize: 11 }}
              />
            )}
            {filteredEvents.map((ev) => (
              <ReferenceLine
                key={ev.Date + ev.Event}
                x={new Date(ev.Date).getTime()}
                stroke={CATEGORY_COLORS[ev.Category] || 'var(--color-ink-muted)'}
                strokeOpacity={0.55}
                strokeWidth={1}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </section>

      <section className="event-panel">
        <h2>Researched events {startDate || endDate ? '(filtered by date range)' : ''}</h2>
        <ul className="event-list">
          {filteredEvents.length === 0 && (
            <li className="event-list__empty">No events match the current filters.</li>
          )}
          {filteredEvents.map((ev) => (
            <li key={ev.Date + ev.Event} className="event-list__item">
              <span className="event-list__dot" style={{ background: CATEGORY_COLORS[ev.Category] }} />
              <div className="event-list__body">
                <div className="event-list__meta">
                  <span className="event-list__date">{ev.Date}</span>
                  <span className="event-list__category">{ev.Category}</span>
                </div>
                <p className="event-list__title">{ev.Event}</p>
                <p className="event-list__desc">{ev.Description}</p>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
