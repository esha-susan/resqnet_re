import re

speech_jsx = r"c:\Users\SREESUTHA\resqnet_re\frontend\src\components\SpeechRecorder.jsx"
speech_css = r"c:\Users\SREESUTHA\resqnet_re\frontend\src\styles\speech.css"

with open(speech_jsx, 'r', encoding='utf-8') as f:
    jsx = f.read()

jsx = jsx.replace('<span className="speech-icon">🎙️</span>', '')
jsx = jsx.replace('🔴 Start Recording', 'Start Recording')
jsx = jsx.replace('⏹ Stop Recording', 'Stop Recording')
jsx = jsx.replace('🔄 Record Again', 'Record Again')
jsx = jsx.replace('🔄 Try Again', 'Try Again')
jsx = jsx.replace('✅ Transcription complete', 'Transcription complete')

with open(speech_jsx, 'w', encoding='utf-8') as f:
    f.write(jsx)

with open(speech_css, 'r', encoding='utf-8') as f:
    css = f.read()

css = css.replace(
'''.speech-recorder {
    background: var(--color-card);
    border: 1px solid rgba(230, 57, 70, 0.2);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
  }''',
'''.speech-recorder {
  background: rgba(30, 41, 59, 0.4);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 85, 255, 0.2);
  border-radius: 20px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}''')

css = css.replace('var(--color-primary)', '#0055FF')
css = css.replace('var(--color-muted)', '#94A3B8')
css = css.replace('var(--color-text)', '#FFFFFF')
css = css.replace('var(--color-card)', 'rgba(30, 41, 59, 0.4)')
css = css.replace('border-radius: 8px', 'border-radius: 12px')

# Make the stop button also look more professional instead of strong red
css = css.replace('background: #e74c3c;', 'background: transparent;\n    border: 1px solid rgba(239, 68, 68, 0.5);\n    color: #ef4444;')

with open(speech_css, 'w', encoding='utf-8') as f:
    f.write(css)

print("Speech components updated!")
