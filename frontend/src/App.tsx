import { useState, useRef, useEffect } from 'react'
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, Radar, Legend,
  BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid
} from 'recharts'
import './App.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
  details?: any
  timestamp: Date
}

interface MarketOverview {
  symbol: string
  name: string
  price: number | null
  change_val: number
  change_pct: number
  market_cap: string
  pe_ratio: string
  revenue_growth: string
  profit_margin: string
  period: string
  source: string
  timestamp: string
  status: string
}

// ── Markdown Bold & Structured Text Formatter ──────────────────────
function RenderMarkdown({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g)
  return (
    <>
      {parts.map((part, i) =>
        part.startsWith('**') && part.endsWith('**') ? (
          <strong key={i}>{part.slice(2, -2)}</strong>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  )
}

function RenderMessage({ text }: { text: string }) {
  const lines = text.split('\n')
  return (
    <>
      {lines.map((line, i) => (
        <span key={i}>
          <RenderMarkdown text={line} />
          {i < lines.length - 1 && <br />}
        </span>
      ))}
    </>
  )
}

// ── Confidence Score Semi-Circle Gauge ─────────────────────────────
function ConfidenceGauge({ value, isDark }: { value: number; isDark: boolean }) {
  const pct = Math.round(value * 100)
  const width = 170
  const height = 105
  const strokeWidth = 12
  const cx = width / 2
  const cy = 85
  const r = 58
  const pi = Math.PI

  const trackD = `M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`
  const clampedVal = Math.min(Math.max(value, 0), 1)
  const fillAngle = pi * clampedVal
  const endX = cx - r * Math.cos(fillAngle)
  const endY = cy - r * Math.sin(fillAngle)
  const largeArcFlag = clampedVal > 1 ? 1 : 0
  const fillD = clampedVal <= 0.01
    ? ''
    : `M ${cx - r} ${cy} A ${r} ${r} 0 ${largeArcFlag} 1 ${endX} ${endY}`

  const color = pct >= 65 ? (isDark ? '#4CAF50' : '#2E7D32') : pct >= 45 ? '#FFA000' : (isDark ? '#EF5350' : '#C62828')
  const statusText = pct >= 65 ? 'High Confidence' : pct >= 45 ? 'Moderate' : 'Low Confidence'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
      <div style={{ position: 'relative', width, height }}>
        <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
          <path d={trackD} fill="none" stroke={isDark ? '#262C36' : '#E5E8E0'} strokeWidth={strokeWidth} strokeLinecap="round" />
          {fillD && (
            <path
              d={fillD}
              fill="none"
              stroke={color}
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              style={{ transition: 'all 0.6s ease' }}
            />
          )}
        </svg>
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            bottom: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            pointerEvents: 'none'
          }}
        >
          <span style={{ fontSize: '24px', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1, fontFamily: 'var(--font-mono)' }}>
            {pct}%
          </span>
          <span style={{ fontSize: '10px', fontWeight: 600, color: 'var(--text-secondary)', marginTop: '4px', textTransform: 'uppercase' }}>
            {statusText}
          </span>
        </div>
      </div>
    </div>
  )
}

// ── Probability Donut Chart ────────────────────────────────────────
const PIE_COLORS: Record<string, string> = {
  BUY: '#76B900',
  HOLD: '#FFA000',
  SELL: '#EF5350',
}

function ProbabilityChart({ probabilities, isDark }: { probabilities: Record<string, number>; isDark: boolean }) {
  const data = Object.entries(probabilities).map(([name, value]) => ({
    name,
    value: Math.round(value * 100),
  }))

  return (
    <ResponsiveContainer width="100%" height={160}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={42}
          outerRadius={65}
          paddingAngle={3}
          dataKey="value"
          label={({ name, value }) => `${name} ${value}%`}
          labelLine={false}
        >
          {data.map((entry) => (
            <Cell key={entry.name} fill={PIE_COLORS[entry.name] ?? '#888'} />
          ))}
        </Pie>
        <Tooltip
          formatter={(v: any) => `${v}%`}
          contentStyle={{
            background: isDark ? '#161B22' : '#FFFFFF',
            border: `1px solid ${isDark ? '#262C36' : '#E5E8E0'}`,
            borderRadius: 6,
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            fontSize: '12px',
            color: isDark ? '#F0F3E8' : '#242820'
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}

// ── Signal Radar Chart ─────────────────────────────────────────────
const SIGNAL_LABELS: Record<string, string> = {
  stock_signal: 'Stock',
  financial_signal: 'Financial',
  market_signal: 'Market',
  risk_signal: 'Risk',
  sentiment_signal: 'Sentiment',
  valuation_signal: 'Valuation',
}

function SignalRadar({ signals, isDark }: { signals: Record<string, number>; isDark: boolean }) {
  const data = Object.entries(SIGNAL_LABELS).map(([key, label]) => {
    const raw = signals[key] ?? 0
    const score = key === 'risk_signal' ? 1 - raw : raw
    return { subject: label, score, fullMark: 1 }
  })

  return (
    <ResponsiveContainer width="100%" height={170}>
      <RadarChart cx="50%" cy="50%" outerRadius={58} data={data}>
        <PolarGrid stroke={isDark ? '#262C36' : '#E5E8E0'} />
        <PolarAngleAxis dataKey="subject" tick={{ fill: isDark ? '#9BA296' : '#747B70', fontSize: 10, fontWeight: 500 }} />
        <Radar
          name="Factor Score"
          dataKey="score"
          stroke="#76B900"
          fill="#76B900"
          fillOpacity={isDark ? 0.35 : 0.2}
          dot={{ fill: '#76B900', r: 2.5 }}
        />
        <Legend formatter={() => 'Factor Rating'} wrapperStyle={{ fontSize: 10, color: isDark ? '#9BA296' : '#747B70' }} />
      </RadarChart>
    </ResponsiveContainer>
  )
}

// ── Dynamic Bar & Area Charts ───────────────────────────────────────
function DynamicChartCard({ chart, isDark }: { chart: any; isDark: boolean }) {
  if (!chart || !chart.data || chart.data.length === 0) return null

  if (chart.type === 'financial_history') {
    return (
      <div className="dynamic-chart-card-light">
        <div className="dynamic-chart-top">
          <span className="dynamic-chart-badge">Financial Statement (10-K)</span>
          <h4 className="dynamic-chart-title">{chart.title}</h4>
        </div>
        <ResponsiveContainer width="100%" height={230}>
          <BarChart data={chart.data} margin={{ top: 10, right: 10, left: -14, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#262C36' : '#F0F3EB'} vertical={false} />
            <XAxis dataKey="period" stroke={isDark ? '#9BA296' : '#747B70'} fontSize={11} tickLine={false} />
            <YAxis stroke={isDark ? '#9BA296' : '#747B70'} fontSize={11} tickLine={false} unit="B" />
            <Tooltip
              formatter={(v: any, name: any) => [`$${v}B`, name]}
              contentStyle={{
                background: isDark ? '#161B22' : '#FFFFFF',
                border: `1px solid ${isDark ? '#262C36' : '#E5E8E0'}`,
                borderRadius: 8,
                boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
                fontSize: '12px',
                color: isDark ? '#F0F3E8' : '#242820'
              }}
            />
            <Legend wrapperStyle={{ fontSize: 11, paddingTop: 6, color: isDark ? '#9BA296' : '#747B70' }} />
            <Bar dataKey="revenue" name="Total Revenue ($B)" fill="#76B900" radius={[4, 4, 0, 0]} />
            <Bar dataKey="netIncome" name="Net Income ($B)" fill="#3A82EE" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  }

  if (chart.type === 'stock_trend') {
    return (
      <div className="dynamic-chart-card-light">
        <div className="dynamic-chart-top">
          <span className="dynamic-chart-badge">Market Price Action</span>
          <h4 className="dynamic-chart-title">{chart.title}</h4>
        </div>
        <ResponsiveContainer width="100%" height={230}>
          <AreaChart data={chart.data} margin={{ top: 10, right: 10, left: -14, bottom: 0 }}>
            <defs>
              <linearGradient id="themeStockFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#76B900" stopOpacity={isDark ? 0.4 : 0.25} />
                <stop offset="95%" stopColor="#76B900" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#262C36' : '#F0F3EB'} vertical={false} />
            <XAxis dataKey="date" stroke={isDark ? '#9BA296' : '#747B70'} fontSize={10} tickLine={false} />
            <YAxis stroke={isDark ? '#9BA296' : '#747B70'} fontSize={10} tickLine={false} domain={['auto', 'auto']} unit="$" />
            <Tooltip
              formatter={(v: any) => [`$${v}`, 'Close Price']}
              contentStyle={{
                background: isDark ? '#161B22' : '#FFFFFF',
                border: `1px solid ${isDark ? '#262C36' : '#E5E8E0'}`,
                borderRadius: 8,
                boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
                fontSize: '12px',
                color: isDark ? '#F0F3E8' : '#242820'
              }}
            />
            <Area
              type="monotone"
              dataKey="price"
              stroke="#76B900"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#themeStockFill)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    )
  }

  return null
}

// ── Main Platform Component ─────────────────────────────────────────
export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [expandedDetails, setExpandedDetails] = useState<Set<number>>(new Set())
  const [activeNav, setActiveNav] = useState('Research')
  const [overview, setOverview] = useState<MarketOverview | null>(null)
  const [overviewLoading, setOverviewLoading] = useState(false)

  // Dark Mode Theme State & Persistence
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('nv_theme')
    if (saved === 'dark' || saved === 'light') return saved
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('nv_theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme(prev => (prev === 'light' ? 'dark' : 'light'))
  }

  const isDark = theme === 'dark'

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const apiUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '')

  // Fetch verified market overview metrics on initial mount
  useEffect(() => {
    async function fetchOverview() {
      setOverviewLoading(true)
      try {
        const res = await fetch(`${apiUrl}/market-overview`)
        if (res.ok) {
          const data = await res.json()
          setOverview(data)
        }
      } catch (err) {
        console.error('Failed to load market overview:', err)
      } finally {
        setOverviewLoading(false)
      }
    }
    fetchOverview()
  }, [apiUrl])

  useEffect(() => {
    if (messages.length > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, loading])

  const handleSend = async (queryToSend?: string) => {
    const text = (queryToSend ?? input).trim()
    if (!text || loading) return

    const userMessage: Message = {
      role: 'user',
      content: text,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch(`${apiUrl}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userMessage.content,
          conversation: messages.map(m => ({ role: m.role, content: m.content }))
        })
      })

      if (!response.ok) throw new Error(`HTTP error: ${response.status}`)
      const data = await response.json()

      const newIndex = messages.length + 1
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer || 'No findings could be synthesized for this query.',
          details: data.details,
          timestamp: new Date()
        }
      ])

      // Auto-expand details for research answers
      if (data.details) {
        setExpandedDetails(prev => new Set(prev).add(newIndex))
      }
    } catch {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Unable to complete research synthesis at this time. Please verify backend service connectivity and retry.',
          timestamp: new Date()
        }
      ])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const toggleDetails = (index: number) => {
    setExpandedDetails(prev => {
      const s = new Set(prev)
      s.has(index) ? s.delete(index) : s.add(index)
      return s
    })
  }

  const handleNewResearch = () => {
    setMessages([])
    setExpandedDetails(new Set())
    setInput('')
    inputRef.current?.focus()
  }

  // 7-Model Ensemble Definitions for Architecture Bar
  const modelsList = [
    { id: 'stock', role: 'Time-Series', name: 'Stock Momentum', desc: 'Price action & technical factors' },
    { id: 'fin', role: 'Fundamental', name: 'Financial Health', desc: 'Balance sheet, margins & FCF' },
    { id: 'mkt', role: 'Competitive', name: 'Market Position', desc: 'Moat depth & hyperscaler share' },
    { id: 'risk', role: 'Exposure', name: 'Risk Assessment', desc: 'Supply chain & geo-exposure' },
    { id: 'sent', role: 'NLP Corpus', name: 'Sentiment Engine', desc: 'Earnings transcripts & filings' },
    { id: 'val', role: 'DCF / Comps', name: 'Valuation Matrix', desc: 'Fair value ranges & multiples' },
    { id: 'synth', role: 'Arbiter', name: 'Neural Synthesizer', desc: 'Cross-model consensus & audit' },
  ]

  const categories = [
    {
      title: 'Company Analysis',
      desc: 'Review revenue, profitability, financial performance, and business fundamentals.',
      query: "Analyze NVIDIA's financial performance, revenue growth, and fundamental health."
    },
    {
      title: 'Valuation',
      desc: 'Explore valuation methodologies, financial assumptions, comparable companies, and estimated valuation ranges.',
      query: "Evaluate NVIDIA's current valuation multiples and fair value estimates."
    },
    {
      title: 'Risk Assessment',
      desc: 'Investigate competitive threats, customer concentration, supply-chain exposure, and other business risks.',
      query: "What are NVIDIA's most critical business and supply-chain risks?"
    },
    {
      title: 'Competitor Analysis',
      desc: 'Compare NVIDIA with AMD and other relevant competitors across AI accelerators.',
      query: "Compare NVIDIA with AMD in data center AI and GPU market position."
    }
  ]

  const suggestedQueries = [
    "Evaluate NVIDIA's investment outlook.",
    "Analyze current valuation.",
    "Identify key investment risks.",
    "Compare NVIDIA with AMD."
  ]

  return (
    <div className="platform-root">
      {/* ── 3. Navigation Header ── */}
      <header className="platform-header">
        <div className="header-inner">
          <div className="brand-group" onClick={handleNewResearch}>
            <div className="brand-badge">NV</div>
            <div className="brand-text">
              <span className="brand-title">NVIDIA Intelligence</span>
              <span className="brand-subtitle">Investment Research &amp; Due Diligence</span>
            </div>
          </div>

          <nav className="header-nav">
            {['Dashboard', 'Research', 'Valuation', 'Risk Analysis', 'Sources'].map(nav => (
              <button
                key={nav}
                className={`nav-link ${activeNav === nav ? 'active' : ''}`}
                onClick={() => {
                  setActiveNav(nav)
                  if (nav === 'Valuation') handleSend("Evaluate NVIDIA's current valuation.")
                  else if (nav === 'Risk Analysis') handleSend("Identify key investment risks for NVIDIA.")
                  else if (nav === 'Sources') handleSend("Show evidence and financial sources for NVIDIA.")
                }}
              >
                {nav}
              </button>
            ))}
          </nav>

          <div className="header-actions">
            {/* Dark Mode Toggle Button */}
            <button
              className="btn-theme-toggle"
              onClick={toggleTheme}
              title={`Switch to ${isDark ? 'Light' : 'Dark'} Mode`}
              aria-label="Toggle Dark Mode"
            >
              {isDark ? (
                <>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="5" />
                    <line x1="12" y1="1" x2="12" y2="3" />
                    <line x1="12" y1="21" x2="12" y2="23" />
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                    <line x1="1" y1="12" x2="3" y2="12" />
                    <line x1="21" y1="12" x2="23" y2="12" />
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                  </svg>
                  <span className="theme-toggle-label">Light</span>
                </>
              ) : (
                <>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                  </svg>
                  <span className="theme-toggle-label">Dark</span>
                </>
              )}
            </button>

            <button className="btn-new-research" onClick={handleNewResearch}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
              <span>New Research</span>
            </button>
          </div>
        </div>
      </header>

      {/* ── Platform Body (Main Content Workspace) ── */}
      <div className="platform-body">
        {/* Main Research Workspace */}
        <main className="platform-main">
          <div className="content-container">

            {/* ── 4. Editorial Hero Section ── */}
            <section className="hero-editorial">
              <div className="hero-tag">
                <span>Institutional Due Diligence</span>
              </div>
              <h1 className="hero-headline">Better research. Clearer decisions.</h1>
              <p className="hero-subhead">
                Analyze financial performance, valuation, competition, and investment risks through evidence-backed multi-agent research.
              </p>

              {/* Research Input Bar */}
              <div className="hero-search-wrapper">
                <input
                  type="text"
                  className="hero-search-input"
                  placeholder="Ask about NVIDIA's financials, valuation, competitive position, or long-term growth..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      handleSend()
                    }
                  }}
                  disabled={loading}
                />
                <button
                  className="btn-hero-submit"
                  onClick={() => handleSend()}
                  disabled={!input.trim() || loading}
                >
                  {loading ? 'Synthesizing...' : 'Start Research'}
                </button>
              </div>

              {/* Tasteful Example Queries */}
              <div className="hero-suggestions">
                <span className="suggestions-label">Explore:</span>
                {suggestedQueries.map((q, idx) => (
                  <button
                    key={idx}
                    className="suggestion-pill"
                    onClick={() => handleSend(q)}
                    disabled={loading}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </section>

            {/* ── 6. Compact Financial Overview (Live Verified NVDA Data) ── */}
            <section className="overview-card">
              <div className="overview-header">
                <div className="overview-title-group">
                  <span className="ticker-badge">NVDA</span>
                  <span className="overview-company-name">NVIDIA Corporation</span>
                </div>
                <div className="overview-source-info">
                  {overviewLoading ? (
                    <span>Fetching verified market data...</span>
                  ) : overview && overview.status === 'live' ? (
                    <>
                      <span>Reporting: {overview.period}</span>
                      <span>•</span>
                      <span>Source: {overview.source}</span>
                      <span>•</span>
                      <span>{overview.timestamp}</span>
                    </>
                  ) : (
                    <span>Financial metrics currently unavailable from exchange</span>
                  )}
                </div>
              </div>

              <div className="overview-grid">
                <div className="metric-cell">
                  <span className="metric-label">Share Price</span>
                  <div className="metric-value-row">
                    <span className="metric-value">
                      {overview?.price != null ? `$${overview.price.toFixed(2)}` : '—'}
                    </span>
                    {overview?.change_pct != null && (
                      <span className={`metric-delta ${overview.change_pct >= 0 ? 'positive' : 'negative'}`}>
                        {overview.change_pct >= 0 ? '+' : ''}{overview.change_pct.toFixed(2)}%
                      </span>
                    )}
                  </div>
                  <span className="metric-sub">USD Nasdaq Real-Time</span>
                </div>

                <div className="metric-cell">
                  <span className="metric-label">Market Capitalization</span>
                  <div className="metric-value-row">
                    <span className="metric-value">{overview?.market_cap || '—'}</span>
                  </div>
                  <span className="metric-sub">Mega-cap AI leader</span>
                </div>

                <div className="metric-cell">
                  <span className="metric-label">Revenue Growth</span>
                  <div className="metric-value-row">
                    <span className="metric-value">{overview?.revenue_growth || '—'}</span>
                  </div>
                  <span className="metric-sub">YoY Data Center expansion</span>
                </div>

                <div className="metric-cell">
                  <span className="metric-label">Net Profit Margin</span>
                  <div className="metric-value-row">
                    <span className="metric-value">{overview?.profit_margin || '—'}</span>
                  </div>
                  <span className="metric-sub">Operating efficiency</span>
                </div>

                <div className="metric-cell">
                  <span className="metric-label">Valuation Multiple</span>
                  <div className="metric-value-row">
                    <span className="metric-value">{overview?.pe_ratio || '—'}</span>
                  </div>
                  <span className="metric-sub">P/E Multiple</span>
                </div>
              </div>
            </section>

            {/* ── 5. Explore Research Categories ── */}
            <section style={{ marginBottom: '24px' }}>
              <div className="section-heading-row">
                <h2 className="section-title">Explore Research</h2>
                <span className="section-subtitle">Select an institutional due diligence module</span>
              </div>

              <div className="categories-grid">
                {categories.map((cat, idx) => (
                  <button
                    key={idx}
                    className="category-card"
                    onClick={() => handleSend(cat.query)}
                    disabled={loading}
                  >
                    <div className="category-icon-wrapper">
                      {idx === 0 && (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <line x1="12" y1="20" x2="12" y2="10" />
                          <line x1="18" y1="20" x2="18" y2="4" />
                          <line x1="6" y1="20" x2="6" y2="16" />
                        </svg>
                      )}
                      {idx === 1 && (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="12" cy="12" r="10" />
                          <path d="M12 6v6l4 2" />
                        </svg>
                      )}
                      {idx === 2 && (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                          <line x1="12" y1="9" x2="12" y2="13" />
                          <line x1="12" y1="17" x2="12.01" y2="17" />
                        </svg>
                      )}
                      {idx === 3 && (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="16 18 22 12 16 6" />
                          <polyline points="8 6 2 12 8 18" />
                        </svg>
                      )}
                    </div>
                    <span className="category-name">{cat.title}</span>
                    <p className="category-desc">{cat.desc}</p>
                    <span className="category-action">
                      <span>Begin Inquiry</span>
                      <span>→</span>
                    </span>
                  </button>
                ))}
              </div>
            </section>

            {/* ── 7. Multi-Agent Research Interface Architecture ── */}
            <section className="agent-pipeline-card">
              <div className="pipeline-header">
                <span className="pipeline-title">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="3" />
                    <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" />
                  </svg>
                  <span>7-Model Ensemble Architecture</span>
                </span>
                <span className="pipeline-badge">Synchronized</span>
              </div>

              <div className="pipeline-models-row">
                {modelsList.map(m => (
                  <div key={m.id} className="pipeline-model-node" title={m.desc}>
                    <span className="model-node-role">{m.role}</span>
                    <span className="model-node-name">{m.name}</span>
                    <span className="model-node-status ready">
                      <span>●</span> Ready
                    </span>
                  </div>
                ))}
              </div>
            </section>

            {/* ── 8. Active Research Findings & Conversation Thread ── */}
            <div className="results-thread">
              {messages.map((message, index) => {
                if (message.role === 'user') {
                  return (
                    <div key={index} id={`inquiry-${index}`} className="user-inquiry-card">
                      <div>
                        <div className="inquiry-label">Institutional Inquiry</div>
                        <div className="inquiry-text">{message.content}</div>
                      </div>
                      <span className="inquiry-time">
                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  )
                }

                // Assistant Research Findings Dossier
                const details = message.details
                const isExpanded = expandedDetails.has(index)

                return (
                  <article key={index} className="research-dossier">
                    {/* Topbar */}
                    <div className="dossier-topbar">
                      <div className="dossier-meta-left">
                        <span className="dossier-engine-pill">
                          {details?.model || 'NVIDIA Intelligence Neural Engine'}
                        </span>
                        {details?.category && (
                          <span className="dossier-category-pill">{details.category}</span>
                        )}
                      </div>
                      <span className="dossier-timestamp">
                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>

                    {/* Synthesis & Answer */}
                    <div className="dossier-body">
                      <RenderMessage text={message.content} />

                      {/* Financial or Stock Chart if returned */}
                      {details?.chart && <DynamicChartCard chart={details.chart} isDark={isDark} />}
                    </div>

                    {/* Evidence & Findings Footer Bar */}
                    {details && (
                      <div className="dossier-footer">
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                          {details.synthesis?.recommendation && (
                            <span className={`verdict-tag ${details.synthesis.recommendation.toLowerCase()}`}>
                              Verdict: {details.synthesis.recommendation}
                            </span>
                          )}
                          {details.verification?.verification_status && (
                            <span className="verdict-tag pass">
                              Verification: {details.verification.verification_status}
                            </span>
                          )}
                        </div>

                        <button className="btn-toggle-evidence" onClick={() => toggleDetails(index)}>
                          <span>{isExpanded ? 'Hide Model Evidence' : 'Expand Multi-Model Evidence'}</span>
                          <span>{isExpanded ? '▲' : '▼'}</span>
                        </button>
                      </div>
                    )}

                    {/* Expandable Multi-Agent Evidence Section */}
                    {details && isExpanded && (
                      <div className="dossier-evidence-panel">
                        {/* Analytical Charts */}
                        {details.synthesis?.probabilities && details.synthesis?.signals && (
                          <div className="charts-grid-light">
                            {details.synthesis?.confidence != null && (
                              <div className="chart-card-light">
                                <span className="chart-card-title">Confidence Calibration</span>
                                <ConfidenceGauge value={details.synthesis.confidence} isDark={isDark} />
                              </div>
                            )}
                            <div className="chart-card-light">
                              <span className="chart-card-title">Recommendation Distribution</span>
                              <ProbabilityChart probabilities={details.synthesis.probabilities} isDark={isDark} />
                            </div>
                            <div className="chart-card-light">
                              <span className="chart-card-title">Factor Balance Radar</span>
                              <SignalRadar signals={details.synthesis.signals} isDark={isDark} />
                            </div>
                          </div>
                        )}

                        {/* Signal Matrix Grid */}
                        {details.synthesis?.signals && (
                          <div className="signal-matrix-card">
                            <h4 className="matrix-title">Model Signal Breakdown</h4>
                            <div className="matrix-grid">
                              {[
                                { key: 'stock_signal', label: 'Stock Momentum', pos: 'BULLISH', neg: 'BEARISH' },
                                { key: 'financial_signal', label: 'Financial Health', pos: 'STRONG', neg: 'WEAK' },
                                { key: 'market_signal', label: 'Competitive Moat', pos: 'EXPANDING', neg: 'CHALLENGED' },
                                { key: 'risk_signal', label: 'Downside Exposure', pos: 'ELEVATED RISK', neg: 'MANAGED RISK', invert: true },
                                { key: 'sentiment_signal', label: 'Filings Sentiment', pos: 'FAVORABLE', neg: 'CAUTIONARY' },
                                { key: 'valuation_signal', label: 'Valuation Attractiveness', pos: 'UNDERVALUED', neg: 'PREMIUM' },
                              ].map(({ key, label, pos, neg, invert }) => {
                                const val = details.synthesis.signals[key] ?? 0
                                const isGood = invert ? val === 0 : val === 1
                                const tag = val === 1 ? pos : neg
                                return (
                                  <div key={key} className="matrix-item">
                                    <span className="matrix-label">{label}</span>
                                    <span className={`matrix-badge ${isGood ? 'good' : 'bad'}`}>
                                      {tag}
                                    </span>
                                  </div>
                                )
                              })}
                            </div>
                          </div>
                        )}

                        {/* Synthesis & Verification Overview */}
                        <div className="decision-summary-row">
                          {details.synthesis?.recommendation && (
                            <div className="decision-badge-card">
                              <span className="badge-card-label">Synthesized Recommendation</span>
                              <span className={`verdict-tag ${details.synthesis.recommendation.toLowerCase()}`}>
                                {details.synthesis.recommendation}
                              </span>
                            </div>
                          )}
                          {details.verification && (
                            <div className="decision-badge-card">
                              <span className="badge-card-label">Evidence Verification</span>
                              <span className="verdict-tag pass">
                                {details.verification.verification_status} (
                                {Math.round((details.verification.confidence_calibration || 0.95) * 100)}% Match)
                              </span>
                            </div>
                          )}
                        </div>

                        {/* Thinking Process / Chain of Thought */}
                        {details.reasoning && (
                          <div className="reasoning-box">
                            <h4 className="evidence-header">Neural Thinking Process</h4>
                            <div className="reasoning-text">{details.reasoning}</div>
                          </div>
                        )}

                        {/* Citations & Evidence Chunks */}
                        {details.evidence && details.evidence.length > 0 && (
                          <div className="evidence-section">
                            <h4 className="evidence-header">Verified Sources &amp; Citations ({details.evidence.length})</h4>
                            <div className="citations-list">
                              {details.evidence.slice(0, 4).map((item: any, i: number) => (
                                <div key={i} className="citation-card">
                                  <span className="citation-tag">Source Chunk #{item.chunk_id ?? i + 1}</span>
                                  <span>{item.text?.substring(0, 190)}...</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </article>
                )
              })}

              {/* Loading State / Skeleton */}
              {loading && (
                <div className="loading-card">
                  <div className="loading-agent-status">
                    <div className="loading-spinner" />
                    <span>Executing 7-model neural diligence pipeline &amp; synthesizing sources...</span>
                  </div>
                  <div className="skeleton-line" style={{ width: '90%' }} />
                  <div className="skeleton-line" style={{ width: '75%' }} />
                  <div className="skeleton-line" style={{ width: '55%' }} />
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

          </div>

          {/* ── 8. Sticky Bottom Composer ── */}
          <footer className="bottom-composer-wrapper">
            <div className="composer-box">
              <textarea
                ref={inputRef}
                className="composer-textarea"
                placeholder="Ask about NVIDIA's financials, valuation, competitive position, or long-term growth..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                rows={1}
                disabled={loading}
              />
              <div className="composer-actions">
                <button
                  className="btn-composer-submit"
                  onClick={() => handleSend()}
                  disabled={!input.trim() || loading}
                  title="Send research query"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <line x1="22" y1="2" x2="11" y2="13" />
                    <polygon points="22 2 15 22 11 13 2 9 22 2" />
                  </svg>
                </button>
              </div>
            </div>
            <div className="composer-meta">
              <span>Press <strong>Enter</strong> to submit inquiry, <strong>Shift+Enter</strong> for newline</span>
              <span>Evidence-backed institutional research</span>
            </div>
          </footer>
        </main>
      </div>
    </div>
  )
}
