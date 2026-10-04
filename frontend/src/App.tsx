import { useState, useRef, useEffect } from 'react'
import './App.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
  details?: any
  timestamp: Date
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [expandedDetails, setExpandedDetails] = useState<Set<number>>(new Set())
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8001/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query: userMessage.content,
          conversation: messages.map(m => ({ role: m.role, content: m.content }))
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      // Add 3 second delay to show thinking animation
      await new Promise(resolve => setTimeout(resolve, 3000))

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer || 'I apologize, but I could not generate a response.',
        details: data.details,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      const errorMessage: Message = {
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const toggleDetails = (index: number) => {
    setExpandedDetails(prev => {
      const newSet = new Set(prev)
      if (newSet.has(index)) {
        newSet.delete(index)
      } else {
        newSet.add(index)
      }
      return newSet
    })
  }

  const handleNewChat = () => {
    setMessages([])
    setExpandedDetails(new Set())
  }

  const exampleQuestions = [
    "Should I invest in NVIDIA?",
    "How is NVIDIA financially right now?",
    "What are NVIDIA's biggest risks?",
    "How does NVIDIA compare with competitors?",
    "What's NVIDIA's valuation?",
  ]

  return (
    <div className="chat-app">
      <header className="chat-header">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon"></div>
            <div className="logo-text">
              <h1>NVIDIA Intelligence</h1>
              <p className="tagline">Financial Research Assistant</p>
            </div>
          </div>
          <button className="new-chat-btn" onClick={handleNewChat}>
            New Chat
          </button>
        </div>
      </header>

      <main className="chat-main">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-screen">
              <div className="welcome-content">
                <h2>Welcome to NVIDIA Intelligence</h2>
                <p>Your AI-powered financial research assistant</p>
                <div className="example-questions">
                  <p className="examples-label">Try asking:</p>
                  {exampleQuestions.map((question, index) => (
                    <button
                      key={index}
                      className="example-question"
                      onClick={() => setInput(question)}
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                {message.role === 'assistant' && (
                  <div className="message-avatar">NV</div>
                )}
                <div className="message-bubble">
                  <p className="message-text">{message.content}</p>
                  {message.role === 'assistant' && message.details && (
                    <button
                      className="toggle-details-btn"
                      onClick={() => toggleDetails(index)}
                    >
                      {expandedDetails.has(index) ? 'Hide Details' : 'Show Details'}
                    </button>
                  )}
                  {message.role === 'assistant' && message.details && expandedDetails.has(index) && (
                    <div className="message-details">
                      {message.details.model && (
                        <div className="detail-section">
                          <h4>Active Model Engine</h4>
                          <span className="detail-badge model-badge">
                            🤖 {message.details.model}
                          </span>
                        </div>
                      )}
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
                      {message.details.synthesis?.recommendation && (
                        <div className="detail-section">
                          <h4>Recommendation</h4>
                          <span className={`detail-badge ${message.details.synthesis.recommendation.toLowerCase()}`}>
                            {message.details.synthesis.recommendation}
                          </span>
                        </div>
                      )}
                      {message.details.synthesis?.confidence && (
                        <div className="detail-section">
                          <h4>Confidence</h4>
                          <div className="confidence-bar">
                            <div className="confidence-fill" style={{ width: `${message.details.synthesis.confidence * 100}%` }}></div>
                          </div>
                          <span className="confidence-value">{Math.round(message.details.synthesis.confidence * 100)}%</span>
                        </div>
                      )}
                      {message.details.synthesis?.signals && (
                        <div className="detail-section">
                          <h4>Model Signals</h4>
                          <div className="signals-list">
                            <div className="signal-item">
                              <span>Stock</span>
                              <span className={message.details.synthesis.signals.stock_signal === 1 ? 'positive' : 'negative'}>
                                {message.details.synthesis.signals.stock_signal === 1 ? 'UP' : 'DOWN'}
                              </span>
                            </div>
                            <div className="signal-item">
                              <span>Financial</span>
                              <span className={message.details.synthesis.signals.financial_signal === 1 ? 'positive' : 'negative'}>
                                {message.details.synthesis.signals.financial_signal === 1 ? 'STRONG' : 'WEAK'}
                              </span>
                            </div>
                            <div className="signal-item">
                              <span>Market</span>
                              <span className={message.details.synthesis.signals.market_signal === 1 ? 'positive' : 'negative'}>
                                {message.details.synthesis.signals.market_signal === 1 ? 'OUTPERFORMING' : 'NOT'}
                              </span>
                            </div>
                            <div className="signal-item">
                              <span>Risk</span>
                              <span className={message.details.synthesis.signals.risk_signal === 1 ? 'negative' : 'positive'}>
                                {message.details.synthesis.signals.risk_signal === 1 ? 'HIGH' : 'LOW'}
                              </span>
                            </div>
                          </div>
                        </div>
                      )}
                      {message.details.verification && (
                        <div className="detail-section">
                          <h4>Verification</h4>
                          <span className={`verification-badge ${message.details.verification.verification_status.toLowerCase()}`}>
                            {message.details.verification.verification_status}
                          </span>
                        </div>
                      )}
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
                    <span></span>
                    <span></span>
                    <span></span>
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
          <button
            className="send-button"
            onClick={handleSend}
            disabled={!input.trim() || loading}
          >
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
