// frontend/src/pages/Resources.jsx
// Resource Management Panel.
// Shows all resources and their live status.
// Allows releasing resources from active incidents.

import { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'
import ResourceBadge from '../components/ResourceBadge'
import { fetchResources } from '../api/index'
import '../styles/resources.css'

const RESOURCE_ICONS = {
  ambulance:  '🚑',
  fire_truck: '🚒',
  doctor:     '👨‍⚕️',
  police:     '🚔',
}

function Resources() {
  const [resources, setResources] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => { loadResources() }, [])

  const loadResources = async () => {
    try {
      setLoading(true)
      const data = await fetchResources()
      setResources(data)
    } catch {
      console.error('Failed to load resources')
    } finally {
      setLoading(false)
    }
  }

  // Filter resources by status
  const filtered = filter === 'all'
    ? resources
    : resources.filter(r => r.status === filter)

  // Count by status for the summary bar
  const available = resources.filter(r => r.status === 'available').length
  const busy = resources.filter(r => r.status === 'busy').length

  return (
    <div>
      <Navbar />
      <div className="resources-container">

        <div className="resources-header">
          <h2>🚑 Resource Management</h2>
          <p className="section-sub">Live status of all emergency resources</p>
        </div>

        {/* ── Summary Bar ── */}
        <div className="resource-summary">
          <div className="summary-card">
            <span className="summary-number">{resources.length}</span>
            <span className="summary-label">Total Units</span>
          </div>
          <div className="summary-card available">
            <span className="summary-number">{available}</span>
            <span className="summary-label">Available</span>
          </div>
          <div className="summary-card busy">
            <span className="summary-number">{busy}</span>
            <span className="summary-label">Deployed</span>
          </div>
        </div>

        {/* ── Filter Tabs ── */}
        <div className="resource-filters">
          {['all', 'available', 'busy'].map(f => (
            <button
              key={f}
              className={`filter-tab ${filter === f ? 'active' : ''}`}
              onClick={() => setFilter(f)}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
          <button className="refresh-btn" onClick={loadResources}>
            🔄 Refresh
          </button>
        </div>

        {/* ── Resource Grid ── */}
        {loading ? (
          <div className="loading-state">Loading resources...</div>
        ) : (
          <div className="resource-grid">
            {filtered.map(resource => (
              <div
                key={resource.id}
                className={`resource-card ${resource.status}`}
              >
                <div className="resource-icon">
                  {RESOURCE_ICONS[resource.type] || '🔧'}
                </div>
                <div className="resource-info">
                  <h4>{resource.type.replace('_', ' ').toUpperCase()}</h4>
                  <p className="resource-location">📍 {resource.location}</p>
                </div>
                <div className={`resource-status-dot ${resource.status}`} />
                <span className={`resource-status-text ${resource.status}`}>
                  {resource.status}
                </span>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  )
}

export default Resources