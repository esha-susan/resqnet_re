import os

res_jsx = r"c:\Users\SREESUTHA\resqnet_re\frontend\src\pages\Resources.jsx"
res_css = r"c:\Users\SREESUTHA\resqnet_re\frontend\src\styles\resources.css"

with open(res_jsx, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
'''const RESOURCE_ICONS = {
  ambulance:  '🚑',
  fire_truck: '🚒',
  doctor:     '👨‍⚕️',
  police:     '🚔',
}''',
'''const RESOURCE_ICONS = {
  ambulance: 'AMB',
  fire_truck: 'FIRE',
  doctor: 'MED',
  police: 'POL',
}''')

text = text.replace("<h2>🚑 Resource Management</h2>", "<h2>Resource Management</h2>")
text = text.replace("🔄 Refresh", "Refresh")
text = text.replace("|| '🔧'", "|| 'RES'")
text = text.replace("📍 {resource.location}", "{resource.location}")

with open(res_jsx, 'w', encoding='utf-8') as f:
    f.write(text)

with open(res_css, 'r', encoding='utf-8') as f:
    css = f.read()

css = css.replace(
'''.resources-container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 2rem;
  }''',
'''.resources-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2.5rem 2rem;
  background-color: #0A0C10;
  color: #FFFFFF;
  font-family: 'Inter', system-ui, sans-serif;
  min-height: 100vh;
  position: relative;
}

.resources-container::before {
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

.resources-container::after {
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

.resources-container > * {
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

css = css.replace(
'''.resource-icon {
    font-size: 2rem;
    line-height: 1;
  }''',
'''.resource-icon {
  font-size: 1rem;
  font-weight: 700;
  color: #0055FF;
  background: rgba(0, 85, 255, 0.1);
  padding: 0.5rem;
  border-radius: 8px;
  line-height: 1;
  min-width: 48px;
  text-align: center;
}''')

css = css.replace(
'''.resource-card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
  backdrop-filter: blur(12px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    position: relative;
    transition: border-color 0.2s;
  }''',
'''.resource-card {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  backdrop-filter: blur(12px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
  transition: all 0.3s ease;
  overflow: hidden;
}

.resource-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.5), 0 0 12px rgba(0, 85, 255, 0.1);
}

.resource-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(0, 85, 255, 0.5), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}

.resource-card:hover::before {
  opacity: 1;
}''')

with open(res_css, 'w', encoding='utf-8') as f:
    f.write(css)

print("Resources updated!")
