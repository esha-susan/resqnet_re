// frontend/src/components/ResourceBadge.jsx
// Small badge showing a resource type with an icon.

const RESOURCE_ICONS = {
    ambulance:  '🚑',
    fire_truck: '🚒',
    doctor:     '👨‍⚕️',
    police:     '🚔',
  }
  
  function ResourceBadge({ type, status }) {
    const icon = RESOURCE_ICONS[type] || '🔧'
    return (
      <span className={`resource-badge resource-badge-${status}`}>
        {icon} {type.replace('_', ' ')}
      </span>
    )
  }
  
  export default ResourceBadge