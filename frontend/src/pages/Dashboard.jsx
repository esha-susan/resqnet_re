// frontend/src/pages/Dashboard.jsx
// Single file, renders completely differently based on role.
// Data is already filtered by the backend — no frontend keyword guessing.

import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Navbar from '../components/Navbar'
import PriorityBadge from '../components/PriorityBadge'
import { fetchDashboardStats } from '../api/index'
import {
  PieChart, Pie, Cell,
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer
} from 'recharts'
import '../styles/dashboard.css'

// ── Constants ─────────────────────────────────────────────────────────────────

const PRIORITY_COLORS = {
  critical: '#ef4444',
  high:     '#f59e0b',
  medium:   '#eab308',
  low:      '#10b981',
}

const ROLE_CONFIG = {
  admin:     { label: 'Command Center',    color: '#0055FF', icon: '', accent: 'rgba(0,85,255,0.15)'   },
  police:    { label: 'Police Dashboard',  color: '#6366f1', icon: '', accent: 'rgba(99,102,241,0.15)' },
  ambulance: { label: 'Ambulance Hub',     color: '#ef4444', icon: '', accent: 'rgba(239,68,68,0.15)'  },
  fire_truck:{ label: 'Fire & Rescue Hub', color: '#f97316', icon: '', accent: 'rgba(249,115,22,0.15)' },
  doctor:    { label: 'Medical Dashboard', color: '#10b981', icon: '', accent: 'rgba(16,185,129,0.15)' },
}

const TOOLTIP_STYLE = {
  contentStyle: {
    backgroundColor: 'rgba(15,23,42,0.95)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '8px',
  },
  itemStyle: { color: '#E2E8F0' },
}

// ── Icons ─────────────────────────────────────────────────────────────────────
const Icons = {
  Clipboard: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>,
  Activity:  () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>,
  Phone:     () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>,
  BarChart:  () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>,
  Target:    () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>,
  Truck:     () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>,
  Refresh:   () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>,
  MapPin:    () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>,
  Clock:     () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>,
  Shield:    () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>,
}

// ── Helpers ───────────────────────────────────────────────────────────────────
const formatTime = (date) => date ? date.toLocaleTimeString() : ''
const formatDate = (iso)  => iso  ? new Date(iso).toLocaleString() : ''

// ── Shared sub-components ─────────────────────────────────────────────────────

function RefreshHeader({ title, subtitle, icon, roleColor, roleBadge, lastUpdated, refreshing, onRefresh }) {
  return (
    <div className="db-header">
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.3rem' }}>
          {icon && <span style={{ fontSize: '1.6rem', lineHeight: 1 }}>{icon}</span>}
          <h2 style={{ margin: 0 }}>{title}</h2>
          {roleBadge && (
            <span style={{
              background: `${roleColor}22`,
              color: roleColor,
              border: `1px solid ${roleColor}44`,
              borderRadius: '999px',
              padding: '2px 12px',
              fontSize: '0.72rem',
              fontWeight: 700,
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
            }}>
              {roleBadge}
            </span>
          )}
        </div>
        <p className="db-subtitle">{subtitle}</p>
      </div>
      <div className="db-header-right">
        {lastUpdated && (
          <span className="db-last-updated">Updated: {formatTime(lastUpdated)}</span>
        )}
        <button
          className={`db-refresh-btn ${refreshing ? 'spinning' : ''}`}
          onClick={onRefresh}
          disabled={refreshing}
        >
          <Icons.Refresh /> {refreshing ? 'Refreshing' : 'Refresh'}
        </button>
      </div>
    </div>
  )
}

function IncidentRow({ incident, navigate }) {
  return (
    <div className="db-incident-row" onClick={() => navigate(`/incidents/${incident.id}`)}>
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
  )
}

// ── Responder Dashboard ───────────────────────────────────────────────────────

function ResponderDashboard({ stats, role, profile, navigate, loadStats, refreshing, lastUpdated }) {
  const cfg = ROLE_CONFIG[role] || ROLE_CONFIG.police

  const activeIncidents = stats?.active_incidents || []
  const closedIncidents = stats?.closed_incidents || []
  const myResources     = stats?.resources || { total: 0, available: 0, busy: 0 }
  const myCalls         = stats?.calls     || { total: 0, confirmed: 0, no_answer: 0 }

  // Pie: my incidents by priority — data already scoped by backend
  const priorityData = stats?.priorities ? [
    { name: 'Critical', value: stats.priorities.critical || 0, color: PRIORITY_COLORS.critical },
    { name: 'High',     value: stats.priorities.high     || 0, color: PRIORITY_COLORS.high     },
    { name: 'Medium',   value: stats.priorities.medium   || 0, color: PRIORITY_COLORS.medium   },
    { name: 'Low',      value: stats.priorities.low      || 0, color: PRIORITY_COLORS.low      },
  ].filter(d => d.value > 0) : []

  // Bar: my unit's resources — resource_types already filtered to this role by backend
  const resourceBarData = stats?.resource_types
    ? Object.entries(stats.resource_types).map(([type, counts]) => ({
        name:      type.replace('_', ' '),
        Available: counts.available || 0,
        Deployed:  counts.busy      || 0,
      }))
    : []

  return (
    <div className="db-page-wrapper">
      {/* Role-coloured top accent bar */}
      <div style={{
        height: '3px',
        background: `linear-gradient(90deg, ${cfg.color}, transparent)`,
        position: 'relative', zIndex: 10,
      }} />
      <Navbar />
      <div className="db-container">

        {/* ── Header ── */}
        <RefreshHeader
          title={cfg.label}
          subtitle={`Welcome back, ${profile?.full_name || 'Responder'}. Showing incidents assigned to your unit.`}
          icon={cfg.icon}
          roleColor={cfg.color}
          roleBadge={role.replace('_', ' ')}
          lastUpdated={lastUpdated}
          refreshing={refreshing}
          onRefresh={() => loadStats(true)}
        />

        {/* ── 3-stat strip ── */}
        <div className="db-stats-row" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>

          <div className="db-stat-card clickable" onClick={() => navigate('/incidents')}>
            <div className="db-stat-header">
              <div className="db-stat-icon-wrapper" style={{ background: `${cfg.color}22`, color: cfg.color }}>
                <Icons.Clipboard />
              </div>
              <span className="db-stat-label">My Incidents</span>
            </div>
            <span className="db-stat-number" style={{ color: cfg.color }}>
              {stats?.incidents?.total || 0}
            </span>
            <div className="db-stat-sub">
              <span><span className="db-value-dot dot-orange" />{stats?.incidents?.in_progress || 0} Active</span>
              <span><span className="db-value-dot dot-green"  />{stats?.incidents?.closed      || 0} Closed</span>
            </div>
          </div>

          <div className="db-stat-card">
            <div className="db-stat-header">
              <div className="db-stat-icon-wrapper" style={{ background: 'rgba(16,185,129,0.15)', color: '#10b981' }}>
                <Icons.Truck />
              </div>
              <span className="db-stat-label">My Unit Resources</span>
            </div>
            <span className="db-stat-number" style={{ color: myResources.available > 0 ? '#10b981' : '#ef4444' }}>
              {myResources.available}
            </span>
            <div className="db-stat-sub">
              <span><span className="db-value-dot dot-green" />{myResources.available} Available</span>
              <span><span className="db-value-dot dot-red"   />{myResources.busy}      Deployed</span>
            </div>
          </div>

          <div className="db-stat-card">
            <div className="db-stat-header">
              <div className="db-stat-icon-wrapper" style={{ background: 'rgba(99,102,241,0.15)', color: '#818cf8' }}>
                <Icons.Phone />
              </div>
              <span className="db-stat-label">Dispatch Calls</span>
            </div>
            <span className="db-stat-number">{myCalls.total}</span>
            <div className="db-stat-sub">
              <span><span className="db-value-dot dot-green" />{myCalls.confirmed} Confirmed</span>
              <span><span className="db-value-dot dot-red"   />{myCalls.no_answer} Missed</span>
            </div>
          </div>

        </div>

        {/* ── Charts row ── */}
        <div className="db-middle-row">

          {/* Pie: my incidents by priority */}
          <div className="db-panel">
            <div className="db-panel-header">
              <h3><Icons.Target /> My Incident Priorities</h3>
            </div>
            <div className="db-chart-container">
              {priorityData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={priorityData}
                      cx="50%" cy="50%"
                      innerRadius={60} outerRadius={90}
                      paddingAngle={5} dataKey="value" stroke="none"
                    >
                      {priorityData.map((entry, i) => (
                        <Cell key={i} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip {...TOOLTIP_STYLE} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="db-empty">
                  <Icons.Clipboard />
                  <span>No incidents assigned to your unit yet.</span>
                </div>
              )}
            </div>
            {/* Pie legend */}
            {priorityData.length > 0 && (
              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginTop: '1rem', justifyContent: 'center' }}>
                {priorityData.map(d => (
                  <span key={d.name} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', color: '#94A3B8' }}>
                    <span style={{ width: 8, height: 8, borderRadius: '50%', background: d.color, display: 'inline-block' }} />
                    {d.name} ({d.value})
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Bar: my unit resource availability */}
          <div className="db-panel">
            <div className="db-panel-header">
              <h3><Icons.Truck /> My Unit Resources</h3>
            </div>
            <div className="db-chart-container">
              {resourceBarData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={resourceBarData} margin={{ top: 20, right: 30, left: -20, bottom: 5 }}>
                    <XAxis dataKey="name" stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                    <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} {...TOOLTIP_STYLE} />
                    <Bar dataKey="Available" stackId="a" fill="#10b981" radius={[0, 0, 4, 4]} />
                    <Bar dataKey="Deployed"  stackId="a" fill={cfg.color} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="db-empty">
                  <Icons.Truck />
                  <span>No resource data available.</span>
                </div>
              )}
            </div>
            {/* Bar legend */}
            {resourceBarData.length > 0 && (
              <div style={{ display: 'flex', gap: '1.5rem', marginTop: '1rem', justifyContent: 'center' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', color: '#94A3B8' }}>
                  <span style={{ width: 10, height: 10, borderRadius: '2px', background: '#10b981', display: 'inline-block' }} />
                  Available
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', color: '#94A3B8' }}>
                  <span style={{ width: 10, height: 10, borderRadius: '2px', background: cfg.color, display: 'inline-block' }} />
                  Deployed
                </span>
              </div>
            )}
          </div>

        </div>

        {/* ── Active + Closed incident panels ── */}
        <div className="db-bottom-row">

          <div className="db-panel">
            <div className="db-panel-header">
              <h3>My Active Operations</h3>
              <button className="db-see-all" style={{ color: cfg.color }} onClick={() => navigate('/incidents')}>
                See all
              </button>
            </div>
            {activeIncidents.length === 0 ? (
              <div className="db-empty">
                <Icons.Activity />
                <span>No active incidents assigned to your unit.</span>
              </div>
            ) : (
              <div className="db-incident-list">
                {activeIncidents.map(i => (
                  <IncidentRow key={i.id} incident={i} navigate={navigate} />
                ))}
              </div>
            )}
          </div>

          <div className="db-panel">
            <div className="db-panel-header">
              <h3>Recently Resolved</h3>
              <span className="db-last-updated">{closedIncidents.length} closed</span>
            </div>
            {closedIncidents.length === 0 ? (
              <div className="db-empty">
                <Icons.Clipboard />
                <span>No closed incidents yet.</span>
              </div>
            ) : (
              <div className="db-incident-list">
                {closedIncidents.map(i => (
                  <div key={i.id} className="db-incident-row" onClick={() => navigate(`/incidents/${i.id}`)}>
                    <div className="db-incident-info">
                      <span className="db-incident-title">{i.title}</span>
                      <span className="db-incident-meta"><Icons.Clock /> {formatDate(i.updated_at)}</span>
                    </div>
                    <PriorityBadge priority={i.priority} />
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>

        {/* ── Quick actions ── */}
        <div className="db-quick-actions">
          <h3>Quick Actions</h3>
          <div className="db-actions-row">
            <button
              className="db-action-btn primary"
              style={{ background: cfg.color, borderColor: cfg.color, boxShadow: `0 4px 16px ${cfg.color}44` }}
              onClick={() => navigate('/incidents')}
            >
              <Icons.Target /> My Incidents
            </button>
            <button className="db-action-btn" onClick={() => navigate('/resources')}>
              <Icons.Truck /> View Resources
            </button>
            <button className="db-action-btn" onClick={() => loadStats(true)}>
              <Icons.Refresh /> Refresh
            </button>
            <a className="db-action-btn" href="mailto:admin@resqnet.com" style={{ textDecoration: 'none' }}>
              <Icons.Shield /> Contact Admin
            </a>
          </div>
        </div>

      </div>
    </div>
  )
}

// ── Admin Dashboard ───────────────────────────────────────────────────────────

function AdminDashboard({ stats, user, navigate, loadStats, refreshing, lastUpdated }) {
  const priorityData = stats?.priorities ? [
    { name: 'Critical', value: stats.priorities.critical || 0, color: PRIORITY_COLORS.critical },
    { name: 'High',     value: stats.priorities.high     || 0, color: PRIORITY_COLORS.high     },
    { name: 'Medium',   value: stats.priorities.medium   || 0, color: PRIORITY_COLORS.medium   },
    { name: 'Low',      value: stats.priorities.low      || 0, color: PRIORITY_COLORS.low      },
  ].filter(d => d.value > 0) : []

  const resourceData = stats?.resource_types
    ? Object.entries(stats.resource_types).map(([type, counts]) => ({
        name:      type.replace('_', ' '),
        Available: counts.available,
        Deployed:  counts.busy,
      }))
    : []

  return (
    <div className="db-page-wrapper">
      <Navbar />
      <div className="db-container">

        <RefreshHeader
          title="Command Center"
          subtitle={<>System Operations active. Operator: <strong>{user?.email}</strong></>}
          lastUpdated={lastUpdated}
          refreshing={refreshing}
          onRefresh={() => loadStats(true)}
        />

        <div className="db-stats-row">
          <div className="db-stat-card clickable" onClick={() => navigate('/incidents')}>
            <div className="db-stat-header">
              <div className="db-stat-icon-wrapper"><Icons.Clipboard /></div>
              <span className="db-stat-label">Total Incidents</span>
            </div>
            <span className="db-stat-number">{stats?.incidents?.total || 0}</span>
            <div className="db-stat-sub">
              <span><span className="db-value-dot dot-blue"   />{stats?.incidents?.open        || 0} Open</span>
              <span><span className="db-value-dot dot-orange" />{stats?.incidents?.in_progress || 0} Active</span>
              <span><span className="db-value-dot dot-green"  />{stats?.incidents?.closed      || 0} Closed</span>
            </div>
          </div>

          <div className="db-stat-card clickable" onClick={() => navigate('/resources')}>
            <div className="db-stat-header">
              <div className="db-stat-icon-wrapper"><Icons.Activity /></div>
              <span className="db-stat-label">Total Resources</span>
            </div>
            <span className="db-stat-number">{stats?.resources?.total || 0}</span>
            <div className="db-stat-sub">
              <span><span className="db-value-dot dot-green" />{stats?.resources?.available || 0} Available</span>
              <span><span className="db-value-dot dot-red"   />{stats?.resources?.busy      || 0} Deployed</span>
            </div>
          </div>

          <div className="db-stat-card">
            <div className="db-stat-header">
              <div className="db-stat-icon-wrapper"><Icons.Phone /></div>
              <span className="db-stat-label">Call Metrics</span>
            </div>
            <span className="db-stat-number">{stats?.calls?.total || 0}</span>
            <div className="db-stat-sub">
              <span><span className="db-value-dot dot-green" />{stats?.calls?.confirmed || 0} Confirmed</span>
              <span><span className="db-value-dot dot-red"   />{stats?.calls?.no_answer || 0} Missed</span>
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

        <div className="db-middle-row">
          <div className="db-panel">
            <div className="db-panel-header">
              <h3><Icons.Target /> Priority Distribution</h3>
            </div>
            <div className="db-chart-container">
              {priorityData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={priorityData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={5} dataKey="value" stroke="none">
                      {priorityData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} itemStyle={{ color: '#E2E8F0' }} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="db-empty"><Icons.Clipboard /><span>No data</span></div>
              )}
            </div>
          </div>

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
                    <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                    <Bar dataKey="Available" stackId="a" fill="#10b981" radius={[0, 0, 4, 4]} />
                    <Bar dataKey="Deployed"  stackId="a" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="db-empty"><Icons.Truck /><span>No resource data</span></div>
              )}
            </div>
          </div>
        </div>

        <div className="db-bottom-row">
          <div className="db-panel">
            <div className="db-panel-header">
              <h3>Active Operations</h3>
              <button className="db-see-all" onClick={() => navigate('/incidents')}>See all</button>
            </div>
            {!stats?.active_incidents?.length ? (
              <div className="db-empty"><Icons.Activity /> No active operations</div>
            ) : (
              <div className="db-incident-list">
                {stats.active_incidents.map(i => <IncidentRow key={i.id} incident={i} navigate={navigate} />)}
              </div>
            )}
          </div>

          <div className="db-panel">
            <div className="db-panel-header">
              <h3>Resolved Operations</h3>
              <button className="db-see-all" onClick={() => navigate('/reports')}>View logs</button>
            </div>
            {!stats?.closed_incidents?.length ? (
              <div className="db-empty"><Icons.Clipboard /> No recent events</div>
            ) : (
              <div className="db-incident-list">
                {stats.closed_incidents.map(i => (
                  <div key={i.id} className="db-incident-row" onClick={() => navigate(`/incidents/${i.id}`)}>
                    <div className="db-incident-info">
                      <span className="db-incident-title">{i.title}</span>
                      <span className="db-incident-meta"><Icons.Clock /> {formatDate(i.updated_at)}</span>
                    </div>
                    <PriorityBadge priority={i.priority} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="db-quick-actions">
          <h3>Quick Actions</h3>
          <div className="db-actions-row">
            <button className="db-action-btn primary" onClick={() => navigate('/incidents')}><Icons.Target /> Report Incident</button>
            <button className="db-action-btn" onClick={() => navigate('/resources')}><Icons.Truck /> View Resources</button>
            <button className="db-action-btn" onClick={() => navigate('/reports')}><Icons.BarChart /> View Analytics</button>
            <button className="db-action-btn" onClick={() => loadStats(true)}><Icons.Refresh /> Refresh Cache</button>
          </div>
        </div>

      </div>
    </div>
  )
}

// ── Main Dashboard (router) ───────────────────────────────────────────────────

function Dashboard() {
  const { user, role, profile } = useAuth()
  const navigate = useNavigate()

  const [stats,       setStats]       = useState(null)
  const [loading,     setLoading]     = useState(true)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [refreshing,  setRefreshing]  = useState(false)

  const loadStats = useCallback(async (isManual = false) => {
    try {
      if (isManual) setRefreshing(true)
      const data = await fetchDashboardStats()
      setStats(data)
      setLastUpdated(new Date())
    } catch (err) {
      console.error('Failed to load dashboard stats', err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  useEffect(() => { loadStats() }, [loadStats])
  useEffect(() => {
    const interval = setInterval(() => loadStats(), 30000)
    return () => clearInterval(interval)
  }, [loadStats])

  if (loading) {
    return (
      <div className="db-page-wrapper">
        <Navbar />
        <div className="db-loading">
          <div className="db-spinner" />
          <p>Initializing ResQNet...</p>
        </div>
      </div>
    )
  }

  const sharedProps = { stats, navigate, loadStats, refreshing, lastUpdated }

  if (role === 'admin' || !role) {
    return <AdminDashboard {...sharedProps} user={user} />
  }

  return <ResponderDashboard {...sharedProps} role={role} profile={profile} />
}

export default Dashboard