import re

file_path = r"c:\Users\SREESUTHA\resqnet_re\frontend\src\styles\incidents.css"

with open(file_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Replace general root styles
css = css.replace(
'''/* ── Page Layout ── */
.incidents-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    gap: 3rem;
  }''',
'''/* ── Page Layout ── */
.incidents-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2.5rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 3rem;
  background-color: #0A0C10;
  color: #FFFFFF;
  font-family: 'Inter', system-ui, sans-serif;
  min-height: 100vh;
  position: relative;
}

.incidents-container::before {
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

.incidents-container::after {
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

.incident-form-section, .incident-list-section {
  position: relative;
  z-index: 10;
}''')

# Replace form
css = css.replace('background: var(--color-surface);', 'background: rgba(15, 23, 42, 0.6);\n    backdrop-filter: blur(12px);')
css = css.replace('border: 1px solid rgba(255,255,255,0.06);', 'border: 1px solid rgba(255, 255, 255, 0.05);')
css = css.replace('border-radius: var(--radius);', 'border-radius: 20px;\n    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);')
css = css.replace('var(--color-primary)', '#0055FF')
css = css.replace('var(--color-muted)', '#94A3B8')
css = css.replace('var(--color-card)', 'rgba(30, 41, 59, 0.4)')
css = css.replace('var(--color-text)', '#FFFFFF')
css = css.replace('border: 1px solid rgba(255,255,255,0.08);', 'border: 1px solid rgba(255, 255, 255, 0.1);')
css = css.replace('border-radius: 8px;', 'border-radius: 12px;')

# Enhance hover for card
css = css.replace('.incident-card:hover {\n    border-color: rgba(230, 57, 70, 0.3);\n  }',
'''.incident-card:hover {
  border-color: rgba(0, 85, 255, 0.3);
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4), 0 0 12px rgba(0, 85, 255, 0.1);
}

.incident-card::before {
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

.incident-card:hover::before {
  opacity: 1;
}''')

# Enhance card transition
css = css.replace('.incident-card {\n    background: rgba(15, 23, 42, 0.6);\n    backdrop-filter: blur(12px);\n    border: 1px solid rgba(255, 255, 255, 0.05);\n    border-radius: 20px;\n    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);\n    padding: 1.5rem;\n    transition: border-color 0.2s;\n  }',
'''.incident-card {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
  padding: 1.5rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}''')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(css)

print("CSS updated successfully!")
