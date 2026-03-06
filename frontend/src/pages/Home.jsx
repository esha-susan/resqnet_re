// frontend/src/pages/Home.jsx
// Temporary landing page. 
// Checks that frontend is running and can reach the backend.

import { useEffect, useState } from 'react'
import { checkHealth } from '../api/index.js'

function Home() {
  const [backendStatus, setBackendStatus] = useState('Checking...')

  useEffect(() => {
    // On page load, ping the backend health endpoint
    checkHealth()
      .then(data => setBackendStatus(data.message))
      .catch(() => setBackendStatus('❌ Backend not reachable'))
  }, [])

  return (
    <div className="home-container">
      <div className="home-card">
        <h1>🚨 ResQNet</h1>
        <p className="subtitle">AI Disaster Communication & Resource Management</p>
        <div className="status-box">
          <span className="status-label">Backend Status:</span>
          <span className="status-value">{backendStatus}</span>
        </div>
      </div>
    </div>
  )
}

export default Home