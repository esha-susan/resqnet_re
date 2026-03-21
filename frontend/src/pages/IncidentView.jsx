// frontend/src/pages/IncidentView.jsx
// Detailed view of a single incident.
// Shows assigned resources, call logs, and close/release controls.

import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import PriorityBadge from '../components/PriorityBadge'
import {
  fetchIncidentById,
  fetchIncidentResources,
  fetchCallLogs,
  releaseResource,
  closeIncident
} from '../api/index'
import '../styles/incidentview.css'

const RESOURCE_ICONS = {
  ambulance:  '🚑',
  fire_truck: '🚒',
  doctor:     '👨‍⚕️',
  police:     '🚔',
}

function IncidentView() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [incident, setIncident] = useState(null)
  const [resources, setResources] = useState([])
  const [callLogs, setCallLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [closing, setClosing] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    loadAll()
  }, [id])

  const loadAll = async () => {
    try {
      setLoading(true)
      const [inc, res, calls] = await Promise.all([
        fetchIncidentById(id),
        fetchIncidentResources(id),
        fetchCallLogs(id)
      ])
      setIncident(inc)
      setResources(res)
      setCallLogs(calls)
    } catch {
      setError('Failed to load incident details')
    } finally {
      setLoading(false)
    }
  }

  const handleReleaseResource = async (resourceId) => {
    try {
      await releaseResource(resourceId, id)
      setSuccess('✅ Resource released successfully')
      setTimeout(() => setSuccess(''), 3000)
      const updated = await fetchIncidentResources(id)
      setResources(updated)
    } catch {
      setError('Failed to release resource')
    }
  }

  const handleCloseIncident = async () => {
    if (!window.confirm(
      'Close this incident? All remaining resources will be released.'
    )) return

    setClosing(true)
    setError('')

    try {
      const result = await closeIncident(id)
      setIncident(result.incident)
      setResources([])
      setSuccess(
        `✅ Incident closed. ${result.resources_released} resources released.`
      )
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to close incident')
    } finally {
      setClosing(false)
    }
  }

  const formatDate = (iso) => {
    if (!iso) return 'Unknown'
    return new Date(iso).toLocaleString()
  }

  // ── Loading state ──
  if (loading) {
    return (
      <div>
        <Navbar />
        <div className="iv-container">
          <div className="loading-state">Loading incident...</div>
        </div>
      </div>
    )
  }

  // ── Not found state ──
  if (!incident) {
    return (
      <div>
        <Navbar />
        <div className="iv-container">
          <div className="iv-error">Incident not found.</div>
        </div>
      </div>
    )
  }

  return (
    <div>
      <Navbar />
      <div className="iv-container">

        {/* ── Back Button ── */}
        <button className="iv-back" onClick={() => navigate('/incidents')}>
          ← Back to Incidents
        </button>

        {error && <div className="iv-alert error">{error}</div>}
        {success && <div className="iv-alert success">{success}</div>}

        {/* ── Incident Header ── */}
        <div className="iv-header">
          <div className="iv-title-row">
            <h2>{incident.title}</h2>
            <PriorityBadge priority={incident.priority} />
          </div>
          <div className="iv-meta">
            <span>📍 {incident.location}</span>
            <span className={`iv-status iv-status-${incident.status}`}>
              ● {incident.status.replace('_', ' ')}
            </span>
            <span>🕐 {formatDate(incident.created_at)}</span>
          </div>
          <p className="iv-description">{incident.description}</p>
        </div>

        {/* ── Resources Section ── */}
        <div className="iv-section">
          <div className="iv-section-header">
            <h3>🚑 Assigned Resources</h3>
            <span className="iv-count">{resources.length} active</span>
          </div>

          {resources.length === 0 ? (
            <div className="iv-empty">
              No active resources — all have been released.
            </div>
          ) : (
            <div className="iv-resource-list">
              {resources.map(item => (
                <div key={item.id} className="iv-resource-card">
                  <span className="iv-resource-icon">
                    {RESOURCE_ICONS[item.resources?.type] || '🔧'}
                  </span>
                  <div className="iv-resource-info">
                    <span className="iv-resource-type">
                      {item.resources?.type?.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className="iv-resource-location">
                      📍 {item.resources?.location}
                    </span>
                  </div>
                  <span className="iv-assigned-time">
                    Assigned: {formatDate(item.assigned_at)}
                  </span>
                  {incident.status !== 'closed' && (
                    <button
                      className="iv-release-btn"
                      onClick={() => handleReleaseResource(item.resources?.id)}
                    >
                      Release
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ── Call Logs Section ── */}
        <div className="iv-section">
          <div className="iv-section-header">
            <h3>📞 Call Logs</h3>
            <span className="iv-count">{callLogs.length} calls</span>
          </div>

          {callLogs.length === 0 ? (
            <div className="iv-empty">No calls made yet.</div>
          ) : (
            <div className="iv-call-list">
              {callLogs.map(log => (
                <div key={log.id} className="iv-call-card">
                  <div className="iv-call-info">
                    <span className="iv-call-name">{log.responder_name}</span>
                    <span className="iv-call-phone">{log.phone}</span>
                  </div>
                  <span className={`iv-call-status iv-call-${log.status}`}>
                    {log.status}
                  </span>
                  <span className="iv-call-time">
                    {formatDate(log.created_at)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ── Close Incident Button ── */}
        {incident.status !== 'closed' && (
          <div className="iv-close-section">
            <div className="iv-close-info">
              <h4>Close This Incident</h4>
              <p>
                This will release all remaining resources and mark
                the incident as resolved. This action cannot be undone.
              </p>
            </div>
            <button
              className="iv-close-btn"
              onClick={handleCloseIncident}
              disabled={closing}
            >
              {closing ? 'Closing...' : '✅ Close Incident'}
            </button>
          </div>
        )}

        {/* ── Closed Banner + View Report ── */}
        {incident.status === 'closed' && (
          <div className="iv-closed-section">
            <div className="iv-closed-banner">
              ✅ This incident has been closed and all resources released.
            </div>
            <button
              className="iv-view-report-btn"
              onClick={() => navigate('/reports')}
            >
              📊 View Report
            </button>
          </div>
        )}

      </div>
    </div>
  )
}

export default IncidentView