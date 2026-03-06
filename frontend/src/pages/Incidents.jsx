// frontend/src/pages/Incidents.jsx
// Main incidents page with two sections:
//   1. Form to create a new incident (top)
//   2. Live list of all incidents (below)

import { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'
import IncidentCard from '../components/IncidentCard'
import { fetchIncidents, createIncident } from '../api/index'
import '../styles/incidents.css'

const PRIORITIES = ['Low', 'Medium', 'High', 'Critical']

function Incidents() {
  // ── State ──
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Form fields
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [location, setLocation] = useState('')
  const [priority, setPriority] = useState('Medium')

  // ── Load incidents on page mount ──
  useEffect(() => {
    loadIncidents()
  }, [])

  const loadIncidents = async () => {
    try {
      setLoading(true)
      const data = await fetchIncidents()
      setIncidents(data)
    } catch (err) {
      setError('Failed to load incidents')
    } finally {
      setLoading(false)
    }
  }

  // ── Submit new incident ──
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setSubmitting(true)

    try {
      const newIncident = await createIncident({
        title,
        description,
        location,
        priority,
      })

      // Prepend new incident to top of list (no need to refetch)
      setIncidents(prev => [newIncident, ...prev])

      // Clear form
      setTitle('')
      setDescription('')
      setLocation('')
      setPriority('Medium')
      setSuccess('✅ Incident reported successfully')

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000)

    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create incident')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      <Navbar />
      <div className="incidents-container">

        {/* ── Report Form ── */}
        <section className="incident-form-section">
          <h2>🚨 Report New Incident</h2>
          <p className="section-sub">Submit a new disaster or emergency event</p>

          {error && <div className="form-error">{error}</div>}
          {success && <div className="form-success">{success}</div>}

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

            <div className="form-group">
              <label>Description *</label>
              <textarea
                placeholder="Describe what is happening in detail..."
                value={description}
                onChange={e => setDescription(e.target.value)}
                rows={4}
                required
              />
            </div>

            <div className="form-group priority-select-group">
              <label>Priority Level</label>
              <div className="priority-buttons">
                {PRIORITIES.map(p => (
                  <button
                    key={p}
                    type="button"
                    className={`priority-btn priority-btn-${p.toLowerCase()} ${priority === p ? 'selected' : ''}`}
                    onClick={() => setPriority(p)}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>

            <button
              type="submit"
              className="submit-incident-btn"
              disabled={submitting}
            >
              {submitting ? 'Reporting...' : '🚨 Report Incident'}
            </button>
          </form>
        </section>

        {/* ── Incident List ── */}
        <section className="incident-list-section">
          <div className="list-header">
            <h2>📋 Active Incidents</h2>
            <span className="incident-count">{incidents.length} total</span>
          </div>

          {loading ? (
            <div className="loading-state">Loading incidents...</div>
          ) : incidents.length === 0 ? (
            <div className="empty-state">
              <p>No incidents reported yet.</p>
              <p>Use the form above to report the first one.</p>
            </div>
          ) : (
            <div className="incident-list">
              {incidents.map(incident => (
                <IncidentCard key={incident.id} incident={incident} />
              ))}
            </div>
          )}
        </section>

      </div>
    </div>
  )
}

export default Incidents