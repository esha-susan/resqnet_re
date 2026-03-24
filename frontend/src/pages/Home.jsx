// frontend/src/pages/Home.jsx
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { checkHealth } from '../api/index.js'
import '../styles/home.css'

function Home() {
  const [backendStatus, setBackendStatus] = useState('Checking...')
  const [isError, setIsError] = useState(false)

  useEffect(() => {
    // On page load, ping the backend health endpoint
    checkHealth()
      .then(data => {
        setBackendStatus(data.message)
        setIsError(false)
      })
      .catch(() => {
        setBackendStatus('Backend Unreachable')
        setIsError(true)
      })
  }, [])

  return (
    <div className="dribbble-layout">
      {/* Background Graphic Elements */}
      <div className="glow-background"></div>
      <div className="mesh-texture"></div>

      {/* Top Header */}
      <header className="home-header">
        <div className="logo-container">
          <div className="logo-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
          </div>
          ResQNet
        </div>
        <nav className="nav-links">
          {/* Removed as requested */}
        </nav>
        <Link to="/login" className="btn-pill secondary" style={{ padding: '0.6rem 1.5rem', fontSize: '0.9rem' }}>
          Sign In
        </Link>
      </header>

      {/* Main Hero Content */}
      <main className="hero-container">
        {/* Removed small badge as requested */}

        <h1 className="hero-title">
          Empower Disaster Response with <br />
          <span className="accent-font">Our AI</span> <span className="highlight">Intelligence</span>
        </h1>

        <p className="hero-subtitle">
          Advanced communication and resource management platform for emergency teams, providing real-time voice, text, and AI analysis to save lives faster.
        </p>

        {/* Removed Get Started & Access Dashboard Actions as requested */}

        {/* Status Box */}
        <div className="system-status-indicator">
          <span>System Status:</span>
          <span className={`status-value ${isError ? 'error' : ''}`}>
            <div className={`status-pulse ${isError ? 'error' : ''}`}></div>
            {backendStatus}
          </span>
        </div>
      </main>
    </div>
  )
}

export default Home