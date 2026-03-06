// frontend/src/components/PriorityBadge.jsx
// Small colored badge showing incident priority level.
// Reusable — used on incident cards, detail views, etc.

import '../styles/incidents.css'

// Each priority maps to a CSS class with a distinct color
const PRIORITY_CLASSES = {
  Low: 'badge-low',
  Medium: 'badge-medium',
  High: 'badge-high',
  Critical: 'badge-critical',
}

function PriorityBadge({ priority }) {
  return (
    <span className={`priority-badge ${PRIORITY_CLASSES[priority] || 'badge-low'}`}>
      {priority}
    </span>
  )
}

export default PriorityBadge