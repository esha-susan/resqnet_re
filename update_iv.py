import re
import os

iv_jsx = r"c:\Users\SREESUTHA\resqnet_re\frontend\src\pages\IncidentView.jsx"
iv_css = r"c:\Users\SREESUTHA\resqnet_re\frontend\src\styles\incidentview.css"

with open(iv_jsx, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace emojis
text = text.replace("'✅ Resource released successfully'", "'Resource released successfully'")
text = text.replace("'✅ Incident closed.", "'Incident closed.")
text = text.replace("<span>📍 {incident.location}</span>", "<span>{incident.location}</span>")
text = text.replace("● {incident.status.replace('_', ' ')}", "{incident.status.replace('_', ' ')}")
text = text.replace("<span>🕐 {formatDate(incident.created_at)}</span>", "<span>{formatDate(incident.created_at)}</span>")
text = text.replace("<h3>🚑 Assigned Resources</h3>", "<h3>Assigned Resources</h3>")
text = text.replace("📍 {item.resources?.location}", "{item.resources?.location}")
text = text.replace("<h3>📞 Call Logs</h3>", "<h3>Call Logs</h3>")
text = text.replace("'✅ Close Incident'", "'Close Incident'")
text = text.replace("✅ This incident has been closed and all resources released.", "This incident has been closed and all resources released.")
text = text.replace("📊 View Report", "View Report")

# Replace icons rendering
text = re.sub(r'const RESOURCE_ICONS = \{.*?\n\}', 'const RESOURCE_ICONS = {\n  ambulance: "AMB",\n  fire_truck: "FIRE",\n  doctor: "MED",\n  police: "POL",\n}', text, flags=re.DOTALL)
text = text.replace("{RESOURCE_ICONS[item.resources?.type] || '🔧'}", "{RESOURCE_ICONS[item.resources?.type] || 'RES'}")

with open(iv_jsx, 'w', encoding='utf-8') as f:
    f.write(text)

with open(iv_css, 'r', encoding='utf-8') as f:
    css = f.read()

# Replace variables and apply Deep Obsidian
css = css.replace(
'''.iv-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }''',
'''.iv-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2.5rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  background-color: #0A0C10;
  color: #FFFFFF;
  font-family: 'Inter', system-ui, sans-serif;
  min-height: 100vh;
  position: relative;
}

.iv-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  height: 80vh;
  background: radial-gradient(ellipse at center, rgba(0, 85, 255, 0.15) 0%, rgba(10, 12, 16, 0) 70%);
  z-index: 0;
  pointer-events: none;
}

.iv-container::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: radial-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 32px 32px;
  z-index: 1;
  pointer-events: none;
}

.iv-container > * { position: relative; z-index: 10; }''')

css = css.replace('var(--color-surface)', 'rgba(15, 23, 42, 0.6)')
css = css.replace('var(--color-card)', 'rgba(30, 41, 59, 0.4)')
css = css.replace('var(--color-muted)', '#94A3B8')
css = css.replace('var(--color-primary)', '#0055FF')
css = css.replace('border: 1px solid rgba(255,255,255,0.06)', 'border: 1px solid rgba(255, 255, 255, 0.05)')
css = css.replace('border-radius: var(--radius)', 'border-radius: 20px\n    backdrop-filter: blur(12px)\n    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4)')
css = css.replace('var(--color-text)', '#FFFFFF')

css = css.replace(
'''.iv-header {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px
    backdrop-filter: blur(12px)
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
    padding: 2rem;
  }''',
'''.iv-header {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  backdrop-filter: blur(12px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
  padding: 2.5rem;
}''')

css = css.replace(
'''.iv-section {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px
    backdrop-filter: blur(12px)
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
    padding: 1.5rem;
  }''',
'''.iv-section {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  backdrop-filter: blur(12px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
  padding: 2rem;
}''')

with open(iv_css, 'w', encoding='utf-8') as f:
    f.write(css)

print("IncidentView files updated!")
