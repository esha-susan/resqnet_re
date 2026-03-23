// frontend/src/pages/Dashboard.jsx
// Live Command Center Dashboard
// Auto-refreshes every 30 seconds
// Shows real-time stats across all system components

import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Navbar from '../components/Navbar'
import PriorityBadge from '../components/PriorityBadge'
import { fetchDashboardStats } from '../api/index'
import '../styles/dashboard.css'

const RESOURCE_ICONS = {
  ambulance:  '🚑',
  fire_truck: '🚒',
  doctor:     '👨‍⚕️',
  police:     '🚔',
}

function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()

  const [stats, setStats]       = useState(null)
  const [loading, setLoading]   = useState(true)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [refreshing, setRefreshing]   = useState(false)

  const loadStats = useCallback(async (isManual = false) => {
    try {
      if (isManual) setRefreshing(true)
      const data = await fetchDashboardStats()
      setStats(data)
      setLastUpdated(new Date())
    } catch (err) {
      console.error('Failed to load dashboard stats')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  // Load on mount
  useEffect(() => {
    loadStats()
  }, [loadStats])

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => loadStats(), 30000)
    return () => clearInterval(interval)
  }, [loadStats])

  const formatTime = (date) => {
    if (!date) return ''
    return date.toLocaleTimeString()
  }

  const formatDate = (iso) => {
    if (!iso) return ''
    return new Date(iso).toLocaleString()
  }

  if (loading) {
    return (
      <div>
        <Navbar />
        <div className="db-loading">
          <div className="db-spinner" />
          <p>Loading command center...</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <Navbar />
      <div className="db-container">

        {/* ── Header ── */}
        <div className="db-header">
          <div>
            <h2>🚨 Command Center</h2>
            <p className="db-subtitle">
              Welcome back, <strong>{user?.email}</strong>
            </p>
          </div>
          <div className="db-header-right">
            {lastUpdated && (
              <span className="db-last-updated">
                Last updated: {formatTime(lastUpdated)}
              </span>
            )}
            <button
              className={`db-refresh-btn ${refreshing ? 'spinning' : ''}`}
              onClick={() => loadStats(true)}
              disabled={refreshing}
            >
              🔄 {refreshing ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </div>

        {/* ── Top Stats Row ── */}
        <div className="db-stats-row">
          <div
            className="db-stat-card clickable"
            onClick={() => navigate('/incidents')}
          >
            <span className="db-stat-icon">📋</span>
            <span className="db-stat-number">
              {stats?.incidents?.total || 0}
            </span>
            <span className="db-stat-label">Total Incidents</span>
            <div className="db-stat-sub">
              <span className="open">
                {stats?.incidents?.open || 0} open
              </span>
              <span className="inprogress">
                {stats?.incidents?.in_progress || 0} active
              </span>
              <span className="closed">
                {stats?.incidents?.closed || 0} closed
              </span>
            </div>
          </div>

          <div
            className="db-stat-card clickable"
            onClick={() => navigate('/resources')}
          >
            <span className="db-stat-icon">🚑</span>
            <span className="db-stat-number">
              {stats?.resources?.total || 0}
            </span>
            <span className="db-stat-label">Total Resources</span>
            <div className="db-stat-sub">
              <span className="available">
                {stats?.resources?.available || 0} available
              </span>
              <span className="busy">
                {stats?.resources?.busy || 0} deployed
              </span>
            </div>
          </div>

          <div className="db-stat-card">
            <span className="db-stat-icon">📞</span>
            <span className="db-stat-number">
              {stats?.calls?.total || 0}
            </span>
            <span className="db-stat-label">Total Calls</span>
            <div className="db-stat-sub">
              <span className="confirmed">
                {stats?.calls?.confirmed || 0} confirmed
              </span>
              <span className="missed">
                {stats?.calls?.no_answer || 0} no answer
              </span>
            </div>
          </div>

          <div
            className="db-stat-card clickable"
            onClick={() => navigate('/reports')}
          >
            <span className="db-stat-icon">📊</span>
            <span className="db-stat-number">
              {stats?.reports_count || 0}
            </span>
            <span className="db-stat-label">Reports Generated</span>
            <div className="db-stat-sub">
              <span className="closed">View all reports →</span>
            </div>
          </div>
        </div>

        {/* ── Middle Row ── */}
        <div className="db-middle-row">

          {/* ── Priority Breakdown ── */}
          <div className="db-panel">
            <h3>🎯 Incidents by Priority</h3>
            <div className="db-priority-list">
              {[
                {
                  label: 'Critical',
                  count: stats?.priorities?.critical || 0,
                  cls: 'critical'
                },
                {
                  label: 'High',
                  count: stats?.priorities?.high || 0,
                  cls: 'high'
                },
                {
                  label: 'Medium',
                  count: stats?.priorities?.medium || 0,
                  cls: 'medium'
                },
                {
                  label: 'Low',
                  count: stats?.priorities?.low || 0,
                  cls: 'low'
                },
              ].map(item => (
                <div key={item.label} className="db-priority-row">
                  <span className={`db-priority-dot ${item.cls}`} />
                  <span className="db-priority-label">{item.label}</span>
                  <div className="db-priority-bar-wrap">
                    <div
                      className={`db-priority-bar ${item.cls}`}
                      style={{
                        width: stats?.incidents?.total
                          ? `${(item.count / stats.incidents.total) * 100}%`
                          : '0%'
                      }}
                    />
                  </div>
                  <span className="db-priority-count">{item.count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* ── Resource Status by Type ── */}
          <div className="db-panel">
            <h3>🚒 Resources by Type</h3>
            <div className="db-resource-type-list">
              {Object.entries(stats?.resource_types || {}).map(
                ([type, counts]) => (
                  <div key={type} className="db-resource-type-row">
                    <span className="db-resource-type-icon">
                      {RESOURCE_ICONS[type] || '🔧'}
                    </span>
                    <span className="db-resource-type-name">
                      {type.replace('_', ' ')}
                    </span>
                    <div className="db-resource-type-counts">
                      <span className="available-dot">
                        ● {counts.available} available
                      </span>
                      <span className="busy-dot">
                        ● {counts.busy} deployed
                      </span>
                    </div>
                  </div>
                )
              )}
            </div>
          </div>

        </div>

        {/* ── Bottom Row — Active + Closed Incidents ── */}
        <div className="db-bottom-row">

          {/* ── Active Incidents ── */}
          <div className="db-panel">
            <div className="db-panel-header">
              <h3>🔴 Active Incidents</h3>
              <button
                className="db-see-all"
                onClick={() => navigate('/incidents')}
              >
                See all →
              </button>
            </div>

            {stats?.active_incidents?.length === 0 ? (
              <div className="db-empty">
                No active incidents 🎉
              </div>
            ) : (
              <div className="db-incident-list">
                {stats?.active_incidents?.map(incident => (
                  <div
                    key={incident.id}
                    className="db-incident-row"
                    onClick={() => navigate(`/incidents/${incident.id}`)}
                  >
                    <div className="db-incident-info">
                      <span className="db-incident-title">
                        {incident.title}
                      </span>
                      <span className="db-incident-location">
                        📍 {incident.location}
                      </span>
                    </div>
                    <div className="db-incident-right">
                      <PriorityBadge priority={incident.priority} />
                      <span className={`db-incident-status ${incident.status}`}>
                        {incident.status.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* ── Recently Closed ── */}
          <div className="db-panel">
            <div className="db-panel-header">
              <h3>✅ Recently Closed</h3>
              <button
                className="db-see-all"
                onClick={() => navigate('/reports')}
              >
                View reports →
              </button>
            </div>

            {stats?.closed_incidents?.length === 0 ? (
              <div className="db-empty">
                No closed incidents yet
              </div>
            ) : (
              <div className="db-incident-list">
                {stats?.closed_incidents?.map(incident => (
                  <div
                    key={incident.id}
                    className="db-incident-row"
                    onClick={() => navigate(`/incidents/${incident.id}`)}
                  >
                    <div className="db-incident-info">
                      <span className="db-incident-title">
                        {incident.title}
                      </span>
                      <span className="db-incident-time">
                        🕐 {formatDate(incident.updated_at)}
                      </span>
                    </div>
                    <PriorityBadge priority={incident.priority} />
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>

        {/* ── Quick Actions ── */}
        <div className="db-quick-actions">
          <h3>⚡ Quick Actions</h3>
          <div className="db-actions-row">
            <button
              className="db-action-btn primary"
              onClick={() => navigate('/incidents')}
            >
              🚨 Report Incident
            </button>
            <button
              className="db-action-btn"
              onClick={() => navigate('/resources')}
            >
              🚑 View Resources
            </button>
            <button
              className="db-action-btn"
              onClick={() => navigate('/reports')}
            >
              📊 View Reports
            </button>
            <button
              className="db-action-btn"
              onClick={() => loadStats(true)}
            >
              🔄 Refresh Data
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}

export default Dashboard