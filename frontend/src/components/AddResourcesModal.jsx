// frontend/src/components/AddResourcesModal.jsx
// Drop-in modal for manually dispatching extra resources to an open incident.
// Matches the existing incidentview.css dark theme exactly.

import { useState } from 'react'
import { addExtraResources } from '../api/index'
import './addresourcesmodal.css'

// ── Keep in sync with your DB resource types ─────────────────────────────────
const RESOURCE_TYPE_OPTIONS = [
  { value: 'fire_truck', label: '🚒  Fire Truck' },
  { value: 'ambulance',  label: '🚑  Ambulance'  },
  { value: 'doctor',     label: '🩺  Doctor'      },
  { value: 'police',     label: '🚔  Police'      },
]

const RESOURCE_ICONS = {
  ambulance:  'AMB',
  fire_truck: 'FIRE',
  doctor:     'MED',
  police:     'POL',
}

const emptyRow = () => ({ type: 'fire_truck', count: 1, _id: Math.random() })

/**
 * Props:
 *   incidentId  {string}   — the incident to add resources to
 *   onClose     {function} — called when the modal should close
 *   onSuccess   {function} — called with the API result when dispatch succeeds
 */
export default function AddResourcesModal({ incidentId, onClose, onSuccess }) {
  const [rows,        setRows]        = useState([emptyRow()])
  const [submitting,  setSubmitting]  = useState(false)
  const [result,      setResult]      = useState(null)   // success result
  const [error,       setError]       = useState('')

  // ── Row helpers ─────────────────────────────────────────────────────────────
  const addRow = () => setRows(r => [...r, emptyRow()])

  const removeRow = (id) => setRows(r => r.filter(row => row._id !== id))

  const updateRow = (id, field, value) =>
    setRows(r => r.map(row => row._id === id ? { ...row, [field]: value } : row))

  // ── Submit ──────────────────────────────────────────────────────────────────
  const handleSubmit = async () => {
    setError('')
    const payload = rows
      .filter(r => r.type && r.count >= 1)
      .map(r => ({ type: r.type, count: Number(r.count) }))

    if (!payload.length) {
      setError('Add at least one resource before dispatching.')
      return
    }

    setSubmitting(true)
    try {
      const data = await addExtraResources(incidentId, payload)
      setResult(data)
      if (onSuccess) onSuccess(data)
    } catch (err) {
      setError(err.message || 'Failed to dispatch resources.')
    } finally {
      setSubmitting(false)
    }
  }

  // ── Result screen ───────────────────────────────────────────────────────────
  if (result) {
    return (
      <div className="arm-overlay" onClick={onClose}>
        <div className="arm-modal" onClick={e => e.stopPropagation()}>
          <div className="arm-result-header">
            <span className="arm-result-icon">✅</span>
            <h3>Resources Dispatched</h3>
            <p className="arm-result-sub">{result.message}</p>
          </div>

          {result.assigned.length > 0 && (
            <div className="arm-result-section">
              <p className="arm-result-label">Assigned & calling now</p>
              <div className="arm-result-list">
                {result.assigned.map(r => (
                  <div key={r.id} className="arm-result-item arm-result-ok">
                    <span className="arm-mini-icon">
                      {RESOURCE_ICONS[r.type] || 'RES'}
                    </span>
                    <span className="arm-result-type">
                      {r.type.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className="arm-result-loc">{r.location}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.unavailable.length > 0 && (
            <div className="arm-result-section">
              <p className="arm-result-label arm-label-warn">
                Could not fulfil
              </p>
              <div className="arm-result-list">
                {result.unavailable.map((u, i) => (
                  <div key={i} className="arm-result-item arm-result-warn">
                    <span className="arm-mini-icon">
                      {RESOURCE_ICONS[u.type] || 'RES'}
                    </span>
                    <span className="arm-result-type">
                      {u.type.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className="arm-result-reason">{u.reason}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button className="arm-done-btn" onClick={onClose}>
            Done
          </button>
        </div>
      </div>
    )
  }

  // ── Form screen ─────────────────────────────────────────────────────────────
  return (
    <div className="arm-overlay" onClick={onClose}>
      <div className="arm-modal" onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div className="arm-header">
          <div className="arm-header-left">
            <span className="arm-header-icon">🚨</span>
            <div>
              <h3>Add Extra Resources</h3>
              <p>Select types and quantities — responders will be called immediately.</p>
            </div>
          </div>
          <button className="arm-close" onClick={onClose} aria-label="Close">✕</button>
        </div>

        {/* Error banner */}
        {error && <div className="arm-error">{error}</div>}

        {/* Resource rows */}
        <div className="arm-rows">
          {rows.map((row, idx) => (
            <div key={row._id} className="arm-row">
              <span className="arm-row-num">{idx + 1}</span>

              <select
                className="arm-select"
                value={row.type}
                onChange={e => updateRow(row._id, 'type', e.target.value)}
              >
                {RESOURCE_TYPE_OPTIONS.map(opt => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>

              <div className="arm-count-wrap">
                <button
                  className="arm-count-btn"
                  onClick={() => updateRow(row._id, 'count', Math.max(1, row.count - 1))}
                >−</button>
                <input
                  className="arm-count-input"
                  type="number"
                  min={1}
                  max={10}
                  value={row.count}
                  onChange={e =>
                    updateRow(row._id, 'count', Math.max(1, Number(e.target.value)))
                  }
                />
                <button
                  className="arm-count-btn"
                  onClick={() => updateRow(row._id, 'count', Math.min(10, row.count + 1))}
                >+</button>
              </div>

              {rows.length > 1 && (
                <button
                  className="arm-remove"
                  onClick={() => removeRow(row._id)}
                  aria-label="Remove row"
                >✕</button>
              )}
            </div>
          ))}
        </div>

        {/* Add another row */}
        <button className="arm-add-row" onClick={addRow}>
          + Add another resource type
        </button>

        {/* Footer actions */}
        <div className="arm-footer">
          <button className="arm-cancel" onClick={onClose}>Cancel</button>
          <button
            className="arm-dispatch"
            onClick={handleSubmit}
            disabled={submitting}
          >
            {submitting ? 'Dispatching…' : '🚨 Dispatch Resources'}
          </button>
        </div>

      </div>
    </div>
  )
}