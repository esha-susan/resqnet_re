import os

reports_jsx = r"c:\Users\SREESUTHA\resqnet_re\frontend\src\pages\Reports.jsx"
reports_css = r"c:\Users\SREESUTHA\resqnet_re\frontend\src\styles\reports.css"

with open(reports_jsx, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("<h2>📊 Incident Reports</h2>", "<h2>Incident Reports</h2>")
text = text.replace("<p className=\"rd-location\">📍 {rd.incident?.location}</p>", "<p className=\"rd-location\">{rd.incident?.location}</p>")
text = text.replace("<h4>🕐 Timeline</h4>", "<h4>Timeline</h4>")
text = text.replace("⏱ {rd.timeline?.total_response_time}", "{rd.timeline?.total_response_time}")
text = text.replace("<h4>🚑 Resources Deployed</h4>", "<h4>Resources Deployed</h4>")
text = text.replace("<h4>📞 Responder Calls</h4>", "<h4>Responder Calls</h4>")
text = text.replace("<h4>📝 Resolution Summary</h4>", "<h4>Resolution Summary</h4>")

with open(reports_jsx, 'w', encoding='utf-8') as f:
    f.write(text)

with open(reports_css, 'r', encoding='utf-8') as f:
    css = f.read()

css = css.replace(
'''.reports-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}''',
'''.reports-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2.5rem 2rem;
  background-color: #0A0C10;
  color: #FFFFFF;
  font-family: 'Inter', system-ui, sans-serif;
  min-height: 100vh;
  position: relative;
}

.reports-container::before {
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

.reports-container::after {
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

.reports-container > * {
  position: relative;
  z-index: 10;
}''')

css = css.replace('var(--color-surface)', 'rgba(15, 23, 42, 0.6)')
css = css.replace('var(--color-card)', 'rgba(30, 41, 59, 0.4)')
css = css.replace('var(--color-muted)', '#94A3B8')
css = css.replace('var(--color-primary)', '#0055FF')
css = css.replace('border: 1px solid rgba(255,255,255,0.06)', 'border: 1px solid rgba(255, 255, 255, 0.05)')
css = css.replace('border-radius: var(--radius)', 'border-radius: 20px;\n  backdrop-filter: blur(12px);\n  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4)')
css = css.replace('var(--color-text)', '#FFFFFF')

with open(reports_css, 'w', encoding='utf-8') as f:
    f.write(css)

print("Reports files updated!")
