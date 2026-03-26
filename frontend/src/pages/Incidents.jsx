// frontend/src/pages/Incidents.jsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext' // ✅ ADDED
import Navbar from '../components/Navbar'
import IncidentCard from '../components/IncidentCard'
import SpeechRecorder from '../components/SpeechRecorder'
import { fetchIncidents, createIncident, updateIncidentPriority } from '../api/index'
import '../styles/incidents.css'
import '../styles/speech.css'

const PRIORITIES = ['Low', 'Medium', 'High', 'Critical']

function Incidents() {
  const navigate = useNavigate()
  const { role } = useAuth() // ✅ ADDED

  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [location, setLocation] = useState('')

  const [autoPriority, setAutoPriority] = useState(null)
  const [overridePriority, setOverridePriority] = useState(null)
  const [showOverride, setShowOverride] = useState(false)
  const [lastCreatedId, setLastCreatedId] = useState(null)

  useEffect(() => { loadIncidents() }, [])

  const loadIncidents = async () => {
    try {
      setLoading(true)
      const data = await fetchIncidents()
      setIncidents(data)
    } catch {
      setError('Failed to load incidents')
    } finally {
      setLoading(false)
    }
  }

  const handleTranscript = (text) => {
    setDescription(text)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setAutoPriority(null)
    setOverridePriority(null)
    setShowOverride(false)
    setSubmitting(true)

    try {
      const newIncident = await createIncident({
        title,
        description,
        location,
      })

      setAutoPriority(newIncident.priority)
      setLastCreatedId(newIncident.id)
      setShowOverride(true)

      setIncidents(prev => [newIncident, ...prev])

      setTitle('')
      setDescription('')
      setLocation('')

      setSuccess(`Incident reported — Priority auto-assigned: ${newIncident.priority}`)
      setTimeout(() => setSuccess(''), 5000)

    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create incident')
    } finally {
      setSubmitting(false)
    }
  }

  const handleOverride = async (newPriority) => {
    if (!lastCreatedId) return

    try {
      const updated = await updateIncidentPriority(lastCreatedId, newPriority)

      setIncidents(prev =>
        prev.map(inc => inc.id === lastCreatedId ? updated : inc)
      )

      setOverridePriority(newPriority)
      setSuccess(`Priority updated to: ${newPriority}`)
      setTimeout(() => setSuccess(''), 3000)

    } catch {
      setError('Failed to update priority')
    }
  }

  return (
    <div>
      <Navbar />
      <div className="incidents-container">

        {/* ✅ FORM ONLY FOR ADMIN */}
        {role === 'admin' && (
          <section className="incident-form-section">
            <h2 className="section-title">Report New Incident</h2>
            <p className="section-sub">
              Priority is automatically assigned by the AI — you can override it after submission
            </p>

            {error && <div className="form-error">{error}</div>}
            {success && <div className="form-success">{success}</div>}

            {showOverride && autoPriority && (
              <div className="priority-result-box">
                <div className="priority-result-header">
                  <span>AI assigned priority:</span>
                  <span className={`priority-result-badge badge-${autoPriority.toLowerCase()}`}>
                    {overridePriority || autoPriority}
                  </span>
                </div>
                <div className="override-section">
                  <span className="override-label">Override if incorrect:</span>
                  <div className="override-buttons">
                    {PRIORITIES.map(p => (
                      <button
                        key={p}
                        type="button"
                        className={`override-btn override-btn-${p.toLowerCase()} 
                          ${(overridePriority || autoPriority) === p ? 'active' : ''}`}
                        onClick={() => handleOverride(p)}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="incident-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Incident Title *</label>
                  <input
                    type="text"
                    placeholder="e.g. Building Fire on Main Street"
                    value={title}
                    onChange={e => setTitle(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Location *</label>
                  <input
                    type="text"
                    placeholder="e.g. 123 Main St, District 4"
                    value={location}
                    onChange={e => setLocation(e.target.value)}
                    required
                  />
                </div>
              </div>

              <SpeechRecorder
                onTranscript={handleTranscript}
                disabled={submitting}
              />

              <div className="form-group">
                <label>Description *</label>
                <textarea
                  placeholder="Describe what is happening..."
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                  rows={4}
                  required
                />
              </div>

              <div className="ai-notice">
                Priority will be automatically determined
              </div>

              <button
                type="submit"
                className="submit-incident-btn"
                disabled={submitting}
              >
                {submitting ? 'Analyzing & Reporting...' : 'Report Incident'}
              </button>
            </form>
          </section>
        )}

        {/* ✅ INCIDENT LIST (VISIBLE TO ALL) */}
        <section className="incident-list-section">
          <div className="list-header">
            <h2 className="section-title">Active Incidents</h2>
            <span className="incident-count">{incidents.length} total</span>
          </div>

          {loading ? (
            <div className="loading-state">Loading incidents...</div>
          ) : incidents.length === 0 ? (
            <div className="empty-state">
              <p>No incidents reported yet.</p>
              {role === 'admin' && <p>Use the form above to report the first one.</p>}
            </div>
          ) : (
            <div className="incident-list">
              {incidents.map(incident => (
                <div
                  key={incident.id}
                  onClick={() => navigate(`/incidents/${incident.id}`)}
                  style={{ cursor: 'pointer' }}
                >
                  <IncidentCard incident={incident} />
                </div>
              ))}
            </div>
          )}
        </section>

      </div>
    </div>
  )
}

export default Incidents