// frontend/src/pages/Dashboard.jsx
import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Navbar from '../components/Navbar'
import PriorityBadge from '../components/PriorityBadge'
import { fetchDashboardStats } from '../api/index'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import '../styles/dashboard.css'

// Priority colors for consistent branding in charts
const PRIORITY_COLORS = {
  critical: '#ef4444', // Red
  high: '#f59e0b',     // Orange
  medium: '#eab308',   // Yellow
  low: '#10b981'       // Green
}

// Simple functional icons to replace emojis
const Icons = {
  Clipboard: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>,
  Activity: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>,
  Phone: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>,
  BarChart: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>,
  Target: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>,
  Truck: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>,
  Refresh: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>,
  MapPin: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>,
  Clock: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
}

function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()

  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [refreshing, setRefreshing] = useState(false)

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

  useEffect(() => {
    loadStats()
  }, [loadStats])

  useEffect(() => {
    const interval = setInterval(() => loadStats(), 30000)
    return () => clearInterval(interval)
  }, [loadStats])

  const formatTime = (date) => date ? date.toLocaleTimeString() : ''
  const formatDate = (iso) => iso ? new Date(iso).toLocaleString() : ''

  if (loading) {
    return (
      <div className="db-page-wrapper">
        <Navbar />
        <div className="db-loading">
          <div className="db-spinner" />
          <p>Initializing Central Command...</p>
        </div>
      </div>
    )
  }

  // Data mapping for Recharts
  const priorityData = stats?.priorities ? [
    { name: 'Critical', value: stats.priorities.critical || 0, color: PRIORITY_COLORS.critical },
    { name: 'High', value: stats.priorities.high || 0, color: PRIORITY_COLORS.high },
    { name: 'Medium', value: stats.priorities.medium || 0, color: PRIORITY_COLORS.medium },
    { name: 'Low', value: stats.priorities.low || 0, color: PRIORITY_COLORS.low },
  ].filter(d => d.value > 0) : []

  // Resource Chart Data
  const resourceData = stats?.resource_types ? Object.entries(stats.resource_types).map(([type, counts]) => ({
    name: type.replace('_', ' '),
    Available: counts.available,
    Deployed: counts.busy
  })) : []

  return (
    <div className="db-page-wrapper">
      <Navbar />
      <div className="db-container">

        {/* ── Header ── */}
        <div className="db-header">
          <div>
            <h2>Command Center</h2>
            <p className="db-subtitle">
              System Operations active. Operator: <strong>{user?.email}</strong>
            </p>
          </div>
          <div className="db-header-right">
            {lastUpdated && (
              <span className="db-last-updated">
                Updated: {formatTime(lastUpdated)}
              </span>
            )}
            <button
              className={`db-refresh-btn ${refreshing ? 'spinning' : ''}`}
              onClick={() => loadStats(true)}
              disabled={refreshing}
            >
              <Icons.Refresh /> {refreshing ? 'Refreshing' : 'Refresh'}
            </button>
          </div>
        </div>

        {/* ── Top Stats Row ── */}
        <div className="db-stats-row">
          <div className="db-stat-card clickable" onClick={() => navigate('/incidents')}>
            <div className="db-stat-header">
              <div className="db-stat-icon-wrapper"><Icons.Clipboard /></div>
              <span className="db-stat-label">Total Incidents</span>
            </div>
            <span className="db-stat-number">{stats?.incidents?.total || 0}</span>
            <div className="db-stat-sub">
              <span><span className="db-value-dot dot-blue"></span> {stats?.incidents?.open || 0} Open</span>
              <span><span className="db-value-dot dot-orange"></span> {stats?.incidents?.in_progress || 0} Active</span>
              <span><span className="db-value-dot dot-green"></span> {stats?.incidents?.closed || 0} Closed</span>
            </div>
          </div>

          <div className="db-stat-card clickable" onClick={() => navigate('/resources')}>
            <div className="db-stat-header">
              <div className="db-stat-icon-wrapper"><Icons.Activity /></div>
              <span className="db-stat-label">Total Resources</span>
            </div>
            <span className="db-stat-number">{stats?.resources?.total || 0}</span>
            <div className="db-stat-sub">
              <span><span className="db-value-dot dot-green"></span> {stats?.resources?.available || 0} Available</span>
              <span><span className="db-value-dot dot-red"></span> {stats?.resources?.busy || 0} Deployed</span>
            </div>
          </div>

          <div className="db-stat-card">
            <div className="db-stat-header">
              <div className="db-stat-icon-wrapper"><Icons.Phone /></div>
              <span className="db-stat-label">Total Call Metrics</span>
            </div>
            <span className="db-stat-number">{stats?.calls?.total || 0}</span>
            <div className="db-stat-sub">
              <span><span className="db-value-dot dot-green"></span> {stats?.calls?.confirmed || 0} Confirmed</span>
              <span><span className="db-value-dot dot-red"></span> {stats?.calls?.no_answer || 0} Missed</span>
            </div>
          </div>

          <div className="db-stat-card clickable" onClick={() => navigate('/reports')}>
            <div className="db-stat-header">
              <div className="db-stat-icon-wrapper"><Icons.BarChart /></div>
              <span className="db-stat-label">Reports Generated</span>
            </div>
            <span className="db-stat-number">{stats?.reports_count || 0}</span>
            <div className="db-stat-sub">
              <span style={{ color: '#0055FF', fontWeight: 600 }}>Access Intelligence Logs →</span>
            </div>
          </div>
        </div>

        {/* ── Middle Row: Charts ── */}
        <div className="db-middle-row">

          {/* Pie Chart: Priority */}
          <div className="db-panel">
            <div className="db-panel-header">
              <h3><Icons.Target /> Incident Priority Distribution</h3>
            </div>
            <div className="db-chart-container">
              {priorityData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={priorityData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={5}
                      dataKey="value"
                      stroke="none"
                    >
                      {priorityData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                      itemStyle={{ color: '#E2E8F0' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="db-empty">
                  <Icons.Clipboard />
                  <span>No data available</span>
                </div>
              )}
            </div>
          </div>

          {/* Bar Chart: Resources */}
          <div className="db-panel">
            <div className="db-panel-header">
              <h3><Icons.Truck /> Resource Utilization</h3>
            </div>
            <div className="db-chart-container">
              {resourceData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={resourceData} margin={{ top: 20, right: 30, left: -20, bottom: 5 }}>
                    <XAxis dataKey="name" stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip
                      cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                      contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                    />
                    <Bar dataKey="Available" stackId="a" fill="#10b981" radius={[0, 0, 4, 4]} />
                    <Bar dataKey="Deployed" stackId="a" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="db-empty">
                  <Icons.Truck />
                  <span>No resource data</span>
                </div>
              )}
            </div>
          </div>

        </div>

        {/* ── Bottom Row — Active + Closed Incidents ── */}
        <div className="db-bottom-row">

          {/* Active Incidents */}
          <div className="db-panel">
            <div className="db-panel-header">
              <h3>Active Operations</h3>
              <button className="db-see-all" onClick={() => navigate('/incidents')}>See all</button>
            </div>

            {stats?.active_incidents?.length === 0 ? (
              <div className="db-empty">
                <Icons.Activity /> No active operations
              </div>
            ) : (
              <div className="db-incident-list">
                {stats?.active_incidents?.map(incident => (
                  <div key={incident.id} className="db-incident-row" onClick={() => navigate(`/incidents/${incident.id}`)}>
                    <div className="db-incident-info">
                      <span className="db-incident-title">{incident.title}</span>
                      <span className="db-incident-meta">
                        <Icons.MapPin /> {incident.location}
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

          {/* Recently Closed */}
          <div className="db-panel">
            <div className="db-panel-header">
              <h3>Resolved Operations</h3>
              <button className="db-see-all" onClick={() => navigate('/reports')}>View logs</button>
            </div>

            {stats?.closed_incidents?.length === 0 ? (
              <div className="db-empty">
                <Icons.Clipboard /> No recent events
              </div>
            ) : (
              <div className="db-incident-list">
                {stats?.closed_incidents?.map(incident => (
                  <div key={incident.id} className="db-incident-row" onClick={() => navigate(`/incidents/${incident.id}`)}>
                    <div className="db-incident-info">
                      <span className="db-incident-title">{incident.title}</span>
                      <span className="db-incident-meta">
                        <Icons.Clock /> {formatDate(incident.updated_at)}
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
          <h3>Quick Actions</h3>
          <div className="db-actions-row">
            <button className="db-action-btn primary" onClick={() => navigate('/incidents')}>
              <Icons.Target /> Report Incident
            </button>
            <button className="db-action-btn" onClick={() => navigate('/resources')}>
              <Icons.Truck /> View Resources
            </button>
            <button className="db-action-btn" onClick={() => navigate('/reports')}>
              <Icons.BarChart /> View Analytics
            </button>
            <button className="db-action-btn" onClick={() => loadStats(true)}>
              <Icons.Refresh /> Manually Refresh Cache
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}

export default Dashboard