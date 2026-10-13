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

// ── Markdown bold renderer ─────────────────────────────────────────
function RenderMarkdown({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g)
  return (
    <>
      {parts.map((part, i) =>
        part.startsWith('**') && part.endsWith('**')
          ? <strong key={i}>{part.slice(2, -2)}</strong>
          : <span key={i}>{part}</span>
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

// ── Confidence Gauge (SVG arc) ─────────────────────────────────────
function ConfidenceGauge({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const size = 180
  const cx = size / 2
  const cy = size / 2
  const r = 62
  const strokeWidth = 10
  const circumference = 2 * Math.PI * r
  // Render a 220-degree gauge arc for clean modern dial look
  const totalAngle = 220
  const totalArc = (totalAngle / 360) * circumference
  const filledArc = totalArc * Math.min(Math.max(value, 0), 1)
  const rotation = 160 // Starts symmetrically at bottom-left

  const color = pct >= 60 ? '#76B900' : pct >= 40 ? '#ffc107' : '#f44336'
  const statusText = pct >= 60 ? 'HIGH' : pct >= 40 ? 'MODERATE' : 'LOW'

  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <h4 className="chart-label">Confidence Score</h4>
      <div style={{ position: 'relative', width: size, height: size * 0.78, display: 'flex', justifyContent: 'center' }}>
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          style={{ transform: `rotate(${rotation}deg)`, transformOrigin: `${cx}px ${cy}px` }}
        >
          {/* Background Track */}
          <circle
            cx={cx}
            cy={cy}
            r={r}
            fill="none"
            stroke="#262838"
            strokeWidth={strokeWidth}
            strokeDasharray={`${totalArc} ${circumference}`}
            strokeLinecap="round"
          />
          {/* Active Value Arc */}
          <circle
            cx={cx}
            cy={cy}
            r={r}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={`${filledArc} ${circumference}`}
            strokeLinecap="round"
            style={{ transition: 'stroke-dasharray 0.8s ease' }}
          />
        </svg>

        {/* Centered Content */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: size * 0.22,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            pointerEvents: 'none',
          }}
        >
          <span style={{ fontSize: '26px', fontWeight: 800, color, lineHeight: 1 }}>{pct}%</span>
          <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', marginTop: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            {statusText}
          </span>
        </div>
      </div>
    </div>
  )
}

// ── Probability Donut Chart ────────────────────────────────────────
const PIE_COLORS: Record<string, string> = {
  BUY: '#76B900', HOLD: '#ffc107', SELL: '#f44336',
}

function ProbabilityChart({ probabilities }: { probabilities: Record<string, number> }) {
  const data = Object.entries(probabilities).map(([name, value]) => ({
    name, value: Math.round(value * 100),
  }))
  return (
    <div>
      <h4 className="chart-label">Probability Breakdown</h4>
      <ResponsiveContainer width="100%" height={180}>
        <PieChart>
          <Pie data={data} cx="50%" cy="50%" innerRadius={48} outerRadius={72}
            paddingAngle={3} dataKey="value"
            label={({ name, value }) => `${name} ${value}%`} labelLine={false}
          >
            {data.map((entry) => (
              <Cell key={entry.name} fill={PIE_COLORS[entry.name] ?? '#888'} />
            ))}
          </Pie>
          <Tooltip
            formatter={(v: any) => `${v}%`}
            contentStyle={{ background: '#1a1a2e', border: '1px solid #333', borderRadius: 8 }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

// ── Signal Radar Chart ─────────────────────────────────────────────
const SIGNAL_LABELS: Record<string, string> = {
  stock_signal: 'Stock', financial_signal: 'Financial',
  market_signal: 'Market', risk_signal: 'Risk',
  sentiment_signal: 'Sentiment', valuation_signal: 'Valuation',
}

function SignalRadar({ signals }: { signals: Record<string, number> }) {
  const data = Object.entries(SIGNAL_LABELS).map(([key, label]) => {
    const raw = signals[key] ?? 0
    const score = key === 'risk_signal' ? 1 - raw : raw
    return { subject: label, score, fullMark: 1 }
  })
  return (
    <div>
      <h4 className="chart-label">Signal Radar</h4>
      <ResponsiveContainer width="100%" height={200}>
        <RadarChart cx="50%" cy="50%" outerRadius={72} data={data}>
          <PolarGrid stroke="#2a2a3a" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: '#aaa', fontSize: 11 }} />
          <Radar name="Score" dataKey="score" stroke="#76B900" fill="#76B900"
            fillOpacity={0.3} dot={{ fill: '#76B900', r: 3 }} />
          <Legend formatter={() => 'Model Score'} wrapperStyle={{ fontSize: 11, color: '#aaa' }} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}

// ── Signal Bars ────────────────────────────────────────────────────
function SignalBars({ signals }: { signals: Record<string, number> }) {
  const items = [
    { key: 'stock_signal',     label: 'Stock Momentum',   pos: 'UP',            neg: 'DOWN',      invert: false },
    { key: 'financial_signal', label: 'Financial Health', pos: 'STRONG',        neg: 'WEAK',      invert: false },
    { key: 'market_signal',    label: 'Market Position',  pos: 'OUTPERFORMING', neg: 'LAGGING',   invert: false },
    { key: 'risk_signal',      label: 'Risk Level',       pos: 'HIGH RISK',     neg: 'LOW RISK',  invert: true  },
    { key: 'sentiment_signal', label: 'News Sentiment',   pos: 'POSITIVE',      neg: 'NEGATIVE',  invert: false },
    { key: 'valuation_signal', label: 'Valuation',        pos: 'ATTRACTIVE',    neg: 'EXPENSIVE', invert: false },
  ]
  return (
    <div className="signal-bars">
      {items.map(({ key, label, pos, neg, invert }) => {
        const val = signals[key] ?? 0
        const isGood = invert ? val === 0 : val === 1
        const tag = val === 1 ? pos : neg
        return (
          <div key={key} className="signal-bar-row">
            <span className="signal-bar-label">{label}</span>
            <div className="signal-bar-track">
              <div className="signal-bar-fill" style={{
                width: '100%',
                background: isGood ? 'rgba(118,185,0,0.18)' : 'rgba(244,67,54,0.18)',
                borderLeft: `3px solid ${isGood ? '#76B900' : '#f44336'}`,
              }} />
            </div>
            <span className={`signal-bar-tag ${isGood ? 'good' : 'bad'}`}>{tag}</span>
          </div>
        )
      })}
    </div>
  )
}

// ── Interactive Financial & Stock Trend Chart Component ────────────
function DynamicChartCard({ chart }: { chart: any }) {
  if (!chart || !chart.data || chart.data.length === 0) return null

  if (chart.type === 'financial_history') {
    return (
      <div className="dynamic-chart-container">
        <div className="dynamic-chart-header">
          <span className="dynamic-chart-badge">📊 Financial Statement</span>
          <h4 className="dynamic-chart-title">{chart.title}</h4>
        </div>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={chart.data} margin={{ top: 12, right: 16, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#222736" vertical={false} />
            <XAxis dataKey="period" stroke="#8892b0" fontSize={12} tickLine={false} />
            <YAxis stroke="#8892b0" fontSize={11} tickLine={false} unit="B" />
            <Tooltip
              formatter={(v: any, name: any) => [`$${v}B`, name]}
              contentStyle={{ background: '#121626', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 10, boxShadow: '0 8px 24px rgba(0,0,0,0.6)' }}
            />
            <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
            <Bar dataKey="revenue" name="Total Revenue ($B)" fill="#76B900" radius={[6, 6, 0, 0]} />
            <Bar dataKey="netIncome" name="Net Income ($B)" fill="#06b6d4" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  }

  if (chart.type === 'stock_trend') {
    return (
      <div className="dynamic-chart-container">
        <div className="dynamic-chart-header">
          <span className="dynamic-chart-badge">📈 Market Price Action</span>
          <h4 className="dynamic-chart-title">{chart.title}</h4>
        </div>
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={chart.data} margin={{ top: 12, right: 16, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="stockGlow" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#76B900" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#76B900" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#222736" vertical={false} />
            <XAxis dataKey="date" stroke="#8892b0" fontSize={11} tickLine={false} />
            <YAxis stroke="#8892b0" fontSize={11} tickLine={false} domain={['auto', 'auto']} unit="$" />
            <Tooltip
              formatter={(v: any) => [`$${v}`, 'Closing Price']}
              contentStyle={{ background: '#121626', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 10, boxShadow: '0 8px 24px rgba(0,0,0,0.6)' }}
            />
            <Area type="monotone" dataKey="price" stroke="#76B900" strokeWidth={2.5} fillOpacity={1} fill="url(#stockGlow)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    )
  }

  return null
}

// ── Main App ───────────────────────────────────────────────────────
function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [expandedDetails, setExpandedDetails] = useState<Set<number>>(new Set())
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const { innerWidth, innerHeight } = window
      // Normalize between -1 and 1
      const x = (e.clientX / innerWidth - 0.5) * 2
      const y = (e.clientY / innerHeight - 0.5) * 2
      setMousePos({ x, y })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = async () => {
    if (!input.trim() || loading) return
    const userMessage: Message = { role: 'user', content: input.trim(), timestamp: new Date() }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)
    const apiUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '')
    try {
      const response = await fetch(`${apiUrl}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userMessage.content,
          conversation: messages.map(m => ({ role: m.role, content: m.content }))
        }),
      })
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
      const data = await response.json()
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer || 'I apologize, but I could not generate a response.',
        details: data.details,
        timestamp: new Date()
      }])
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'I apologize, but I encountered an error. Please try again.',
        timestamp: new Date()
      }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  const toggleDetails = (index: number) => {
    setExpandedDetails(prev => {
      const s = new Set(prev); s.has(index) ? s.delete(index) : s.add(index); return s
    })
  }

  const exampleQuestions = [
    "Should I invest in NVIDIA?",
    "How is NVIDIA financially right now?",
    "What are NVIDIA's biggest risks?",
    "How does NVIDIA compare with AMD?",
    "What's NVIDIA's valuation?",
  ]

  return (
    <div className="chat-app">
      {/* ── Dynamic Ambient Parallax Orbs & Grid ── */}
      <div className="bg-ambient">
        <div
          className="ambient-orb orb-1"
          style={{
            transform: `translate(${mousePos.x * 25}px, ${mousePos.y * 25}px)`,
          }}
        />
        <div
          className="ambient-orb orb-2"
          style={{
            transform: `translate(${mousePos.x * -35}px, ${mousePos.y * -35}px)`,
          }}
        />
        <div
          className="ambient-orb orb-3"
          style={{
            transform: `translate(${mousePos.x * 20}px, ${mousePos.y * -20}px)`,
          }}
        />
      </div>
      <div className="bg-grid" />

      {/* ── Apple-Inspired Frosted Header ── */}
      <header className="chat-header">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon-wrapper">
              <div className="logo-icon-glow" />
              <div className="logo-icon">NV</div>
            </div>
            <div className="logo-text">
              <h1>
                NVIDIA Intelligence
                <span className="live-pill">Live AI</span>
              </h1>
              <p className="tagline">Neural Financial Reasoning & Diligence Engine</p>
            </div>
          </div>
          <button className="new-chat-btn" onClick={() => { setMessages([]); setExpandedDetails(new Set()) }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            New Chat
          </button>
        </div>
      </header>

      <main className="chat-main">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-screen">
              <div className="welcome-content">
                <div className="welcome-badge">
                  <span>✦</span> Multi-Model Ensemble & Neural Verification Engine
                </div>
                <h2>Next-Gen NVIDIA Due Diligence</h2>
                <p>Synthesizing 7 specialized ML models into verifiable investment decisions.</p>
                <div className="example-questions">
                  <p className="examples-label">Explore Key Inquiries</p>
                  {exampleQuestions.map((q, i) => (
                    <button key={i} className="example-question" onClick={() => setInput(q)}>
                      <span>{q}</span>
                      <span className="example-question-arrow">→</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                {message.role === 'assistant' && <div className="message-avatar">NV</div>}
                <div className="message-bubble">
                  <p className="message-text">
                    <RenderMessage text={message.content} />
                  </p>

                  {/* ── Contextual Financial / Stock Trend Chart ── */}
                  {message.role === 'assistant' && message.details?.chart && (
                    <DynamicChartCard chart={message.details.chart} />
                  )}

                  {message.role === 'assistant' && message.details && (
                    <button className="toggle-details-btn" onClick={() => toggleDetails(index)}>
                      {expandedDetails.has(index) ? '▲ Hide Details' : '▼ Show Details'}
                    </button>
                  )}

                  {message.role === 'assistant' && message.details && expandedDetails.has(index) && (
                    <div className="message-details">

                      {/* Model badge */}
                      <div className="detail-section">
                        <h4>Active Intelligence Engine</h4>
                        <span className="detail-badge model-badge">
                          ⚡ {message.details.model && !message.details.model.toLowerCase().includes('gemma')
                              ? message.details.model
                              : 'NVIDIA Neural Diligence Engine'}
                        </span>
                      </div>

                      {/* ── CHARTS (investment queries only) ── */}
                      {message.details.synthesis?.probabilities && message.details.synthesis?.signals && (
                        <div className="charts-grid">
                          {message.details.synthesis?.confidence != null && (
                            <div className="chart-card">
                              <ConfidenceGauge value={message.details.synthesis.confidence} />
                            </div>
                          )}
                          <div className="chart-card">
                            <ProbabilityChart probabilities={message.details.synthesis.probabilities} />
                          </div>
                          <div className="chart-card">
                            <SignalRadar signals={message.details.synthesis.signals} />
                          </div>
                        </div>
                      )}

                      {/* Signal bars */}
                      {message.details.synthesis?.signals && (
                        <div className="detail-section">
                          <h4>Model Signals</h4>
                          <SignalBars signals={message.details.synthesis.signals} />
                        </div>
                      )}

                      {/* Recommendation + Verification inline */}
                      {(message.details.synthesis?.recommendation || message.details.verification) && (
                        <div className="detail-section inline-row">
                          {message.details.synthesis?.recommendation && (
                            <div>
                              <h4>Recommendation</h4>
                              <span className={`detail-badge ${message.details.synthesis.recommendation.toLowerCase()}`}>
                                {message.details.synthesis.recommendation}
                              </span>
                            </div>
                          )}
                          {message.details.verification && (
                            <div>
                              <h4>Verification</h4>
                              <span className={`verification-badge ${message.details.verification.verification_status.toLowerCase()}`}>
                                {message.details.verification.verification_status}
                              </span>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Thinking process */}
                      {message.details.reasoning && (
                        <div className="detail-section">
                          <h4>Thinking Process</h4>
                          <div className="reasoning-content">
                            {message.details.reasoning.split('\n').map((line: string, i: number) => (
                              <div key={i} className="reasoning-line">{line}</div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Evidence */}
                      {message.details.evidence && message.details.evidence.length > 0 && (
                        <div className="detail-section">
                          <h4>Sources ({message.details.evidence.length})</h4>
                          <div className="evidence-list">
                            {message.details.evidence.slice(0, 3).map((item: any, i: number) => (
                              <div key={i} className="evidence-item">
                                <span className="evidence-id">Source {item.chunk_id}</span>
                                <p className="evidence-text">{item.text?.substring(0, 150)}...</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="message assistant">
              <div className="message-content">
                <div className="message-avatar">NV</div>
                <div className="message-bubble loading">
                  <div className="typing-indicator">
                    <span></span><span></span><span></span>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="chat-footer">
        <div className="input-container">
          <textarea
            ref={inputRef}
            className="chat-input"
            placeholder="Ask about NVIDIA's financials, risks, valuation, or market position..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            rows={1}
            disabled={loading}
          />
          <button className="send-button" onClick={handleSend} disabled={!input.trim() || loading}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
            </svg>
          </button>
        </div>
        <p className="footer-note">Press Enter to send, Shift+Enter for new line</p>
      </footer>
    </div>
  )
}

export default App
