// frontend/src/components/IncidentCard.jsx
// Displays one incident in the list.
// Receives incident data as a prop and renders it cleanly.

import PriorityBadge from './PriorityBadge'
import '../styles/incidents.css'

// Format ISO date string into readable format
function formatDate(isoString) {
  return new Date(isoString).toLocaleString()
}

// Map status to a readable label with color class
const STATUS_CLASSES = {
  open: 'status-open',
  in_progress: 'status-inprogress',
  closed: 'status-closed',
}

function IncidentCard({ incident }) {
  return (
    <div className="incident-card">
      <div className="incident-card-header">
        <h3 className="incident-title">{incident.title}</h3>
        <PriorityBadge priority={incident.priority} />
      </div>

      <p className="incident-description">{incident.description}</p>

      <div className="incident-meta">
        <span className="incident-location">📍 {incident.location}</span>
        <span className={`incident-status ${STATUS_CLASSES[incident.status]}`}>
          ● {incident.status.replace('_', ' ')}
        </span>
      </div>

      <div className="incident-footer">
        <span className="incident-time">🕐 {formatDate(incident.created_at)}</span>
      </div>
    </div>
  )
}

export default IncidentCard