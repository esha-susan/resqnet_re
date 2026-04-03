// frontend/src/pages/IncidentView.jsx
// Role-aware incident detail view.
// Admins: full controls (add resources, release, close)
// Responders: read-only view of their assigned incidents

import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import PriorityBadge from '../components/PriorityBadge'
import AddResourcesModal from '../components/AddResourcesModal'
import { useAuth } from '../context/AuthContext'
import {
  fetchIncidentById,
  fetchIncidentResources,
  fetchCallLogs,
  releaseResource,
  closeIncident
} from '../api/index'
import '../styles/incidentview.css'

const RESOURCE_ICONS = {
  ambulance:  'AMB',
  fire_truck: 'FIRE',
  doctor:     'MED',
  police:     'POL',
}

const ROLE_RESOURCE_MAP = {
  ambulance:  'ambulance',
  fireforce:  'fire_truck',
  doctor:     'doctor',
  police:     'police',
}

function IncidentView() {
  const { id }       = useParams()
  const navigate     = useNavigate()
  const { isAdmin, role }  = useAuth()

  const [incident,     setIncident]     = useState(null)
  const [resources,    setResources]    = useState([])
  const [callLogs,     setCallLogs]     = useState([])
  const [loading,      setLoading]      = useState(true)
  const [closing,      setClosing]      = useState(false)
  const [error,        setError]        = useState('')
  const [success,      setSuccess]      = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [addModalFixedType, setAddModalFixedType] = useState(null)

  useEffect(() => { loadAll() }, [id])

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
      setSuccess('Resource released successfully')
      setTimeout(() => setSuccess(''), 3000)
      setResources(await fetchIncidentResources(id))
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
      setSuccess(`✅ Incident closed. ${result.resources_released} resources released.`)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to close incident')
    } finally {
      setClosing(false)
    }
  }

  const handleResourcesAdded = async (result) => {
    try {
      const [res, calls] = await Promise.all([
        fetchIncidentResources(id),
        fetchCallLogs(id)
      ])
      setResources(res)
      setCallLogs(calls)
    } catch { /* modal shows success already */ }

    setSuccess(`🚨 ${result.total_assigned} extra resource(s) dispatched successfully.`)
    setTimeout(() => setSuccess(''), 5000)
  }

  const formatDate = (iso) => iso ? new Date(iso).toLocaleString() : 'Unknown'

  if (loading) {
    return (
      <div><Navbar />
        <div className="iv-container">
          <div className="loading-state">Loading incident...</div>
        </div>
      </div>
    )
  }

  if (!incident) {
    return (
      <div><Navbar />
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

        {/* ── Back ── */}
        <button className="iv-back" onClick={() => navigate('/incidents')}>
          ← Back to Incidents
        </button>

        {error   && <div className="iv-alert error">{error}</div>}
        {success && <div className="iv-alert success">{success}</div>}

        {/* ── Header ── */}
        <div className="iv-header">
          <div className="iv-title-row">
            <h2>{incident.title}</h2>
            <PriorityBadge priority={incident.priority} />
          </div>
          <div className="iv-meta">
            <span>{incident.location}</span>
            <span className={`iv-status iv-status-${incident.status}`}>
              {incident.status.replace('_', ' ')}
            </span>
            <span>{formatDate(incident.created_at)}</span>
          </div>
          <p className="iv-description">{incident.description}</p>
        </div>

        {/* ── Resources ── */}
        <div className="iv-section">
          <div className="iv-section-header">
            <h3>Assigned Resources</h3>
            <div className="iv-section-header-actions">
              <span className="iv-count">{resources.length} active</span>
              {/* Admin only: Add Resources */}
              {isAdmin && incident.status !== 'closed' && (
                <button
                  className="iv-add-resources-btn"
                  onClick={() => {
                    setAddModalFixedType(null)
                    setShowAddModal(true)
                  }}
                >
                  + Add Resources
                </button>
              )}
              {/* Responder: Request Extra Resource of their own type */}
              {!isAdmin && incident.status !== 'closed' && ROLE_RESOURCE_MAP[role] && (
                <button
                  className="iv-add-resources-btn"
                  onClick={() => {
                    setAddModalFixedType(ROLE_RESOURCE_MAP[role])
                    setShowAddModal(true)
                  }}
                >
                  + Extra Resource
                </button>
              )}
            </div>
          </div>

          {resources.length === 0 ? (
            <div className="iv-empty">No active resources — all have been released.</div>
          ) : (
            <div className="iv-resource-list">
              {resources.map(item => (
                <div key={item.id} className="iv-resource-card">
                  <span className="iv-resource-icon">
                    {RESOURCE_ICONS[item.resources?.type] || 'RES'}
                  </span>
                  <div className="iv-resource-info">
                    <span className="iv-resource-type">
                      {item.resources?.type?.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className="iv-resource-location">
                      {item.resources?.location}
                    </span>
                  </div>
                  <span className="iv-assigned-time">
                    Assigned: {formatDate(item.assigned_at)}
                  </span>
                  {/* Admin or matched role: Release button */}
                  {(isAdmin || ROLE_RESOURCE_MAP[role] === item.resources?.type) && incident.status !== 'closed' && (
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

        {/* ── Call Logs ── */}
        <div className="iv-section">
          <div className="iv-section-header">
            <h3>Call Logs</h3>
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
                  <span className="iv-call-time">{formatDate(log.created_at)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ── Close Incident — Admin only ── */}
        {isAdmin && incident.status !== 'closed' && (
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
              {closing ? 'Closing...' : 'Close Incident'}
            </button>
          </div>
        )}

        {/* ── Responder read-only notice ── */}
        {!isAdmin && incident.status !== 'closed' && (
          <div className="iv-responder-notice">
            <span>👁 You are viewing this incident as a responder. You can only release resources corresponding to your unit.</span>
          </div>
        )}

        {/* ── Closed Banner ── */}
        {incident.status === 'closed' && (
          <div className="iv-closed-section">
            <div className="iv-closed-banner">
              This incident has been closed and all resources released.
            </div>
            {isAdmin && (
              <button
                className="iv-view-report-btn"
                onClick={() => navigate('/reports')}
              >
                View Report
              </button>
            )}
          </div>
        )}

      </div>

      {showAddModal && (
        <AddResourcesModal
          incidentId={id}
          fixedType={addModalFixedType}
          onClose={() => setShowAddModal(false)}
          onSuccess={(result) => {
            handleResourcesAdded(result)
            setShowAddModal(false)
          }}
        />
      )}
    </div>
  )
}

export default IncidentView