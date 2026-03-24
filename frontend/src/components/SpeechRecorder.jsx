// frontend/src/components/SpeechRecorder.jsx
//
// This component handles everything audio-related:
//   1. Requests microphone permission from the browser
//   2. Records audio using the MediaRecorder API (built into all browsers)
//   3. Sends the audio blob to Flask for Whisper transcription
//   4. Returns the transcript text to the parent via onTranscript() callback
//
// The parent (Incidents.jsx) just receives the text and fills the form.
// This component doesn't know about incidents — clean separation.

import { useState, useRef } from 'react'
import { transcribeAudio } from '../api/index'
import '../styles/speech.css'

function SpeechRecorder({ onTranscript, disabled }) {
  const [status, setStatus] = useState('idle')
  // idle | requesting | recording | processing | done | error
  
  const [error, setError] = useState('')
  const [transcript, setTranscript] = useState('')
  const [duration, setDuration] = useState(0)
  
  // Refs persist across renders without causing re-renders
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])    // collects audio data chunks during recording
  const timerRef = useRef(null)

  // ── Start Recording ──
  const startRecording = async () => {
    setError('')
    setTranscript('')
    setStatus('requesting')

    try {
      // Ask browser for microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      setStatus('recording')
      setDuration(0)
      audioChunksRef.current = []

      // Start duration timer
      timerRef.current = setInterval(() => {
        setDuration(prev => prev + 1)
      }, 1000)

      // Create MediaRecorder with the microphone stream
      // webm is the most widely supported format for browser recording
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      })
      mediaRecorderRef.current = mediaRecorder

      // Every time audio data is available, collect it
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data)
        }
      }

      // When recording stops, process the audio
      mediaRecorder.onstop = async () => {
        clearInterval(timerRef.current)
        
        // Stop all microphone tracks to release the mic
        stream.getTracks().forEach(track => track.stop())
        
        // Combine all chunks into one Blob
        const audioBlob = new Blob(audioChunksRef.current, { 
          type: 'audio/webm' 
        })
        
        await processAudio(audioBlob)
      }

      // Start recording, collect data every 250ms
      mediaRecorder.start(250)

    } catch (err) {
      clearInterval(timerRef.current)
      
      if (err.name === 'NotAllowedError') {
        setError('Microphone permission denied. Please allow microphone access.')
      } else {
        setError(`Could not start recording: ${err.message}`)
      }
      setStatus('error')
    }
  }

  // ── Stop Recording ──
  const stopRecording = () => {
    if (mediaRecorderRef.current && status === 'recording') {
      mediaRecorderRef.current.stop()   // triggers onstop handler above
      setStatus('processing')
    }
  }

  // ── Send to Whisper ──
  const processAudio = async (audioBlob) => {
    try {
      setStatus('processing')
      
      const result = await transcribeAudio(audioBlob)
      
      setTranscript(result.transcript)
      setStatus('done')
      
      // Send transcript up to the parent component
      onTranscript(result.transcript)
      
    } catch (err) {
      setError('Transcription failed. Please try again or type manually.')
      setStatus('error')
    }
  }

  // ── Format timer display ──
  const formatDuration = (secs) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0')
    const s = (secs % 60).toString().padStart(2, '0')
    return `${m}:${s}`
  }

  // ── Reset to idle ──
  const reset = () => {
    setStatus('idle')
    setError('')
    setTranscript('')
    setDuration(0)
  }

  return (
    <div className="speech-recorder">
      <div className="speech-header">
        
        <div>
          <h4>Voice Report</h4>
          <p>Record your incident description — it will be auto-transcribed</p>
        </div>
      </div>

      {/* ── Controls ── */}
      <div className="speech-controls">
        {status === 'idle' && (
          <button
            type="button"
            className="record-btn"
            onClick={startRecording}
            disabled={disabled}
          >
            Start Recording
          </button>
        )}

        {status === 'requesting' && (
          <div className="speech-status">
            <span className="pulse-dot" />
            Requesting microphone access...
          </div>
        )}

        {status === 'recording' && (
          <div className="recording-active">
            <div className="recording-indicator">
              <span className="pulse-dot red" />
              <span>Recording — {formatDuration(duration)}</span>
            </div>
            <button
              type="button"
              className="stop-btn"
              onClick={stopRecording}
            >
              Stop Recording
            </button>
          </div>
        )}

        {status === 'processing' && (
          <div className="speech-status">
            <span className="spinner" />
            Transcribing with Whisper AI...
          </div>
        )}

        {status === 'done' && (
          <div className="speech-done">
            <div className="speech-success">
              Transcription complete — description has been filled below
            </div>
            <button
              type="button"
              className="record-again-btn"
              onClick={reset}
            >
              Record Again
            </button>
          </div>
        )}

        {status === 'error' && (
          <div className="speech-done">
            <div className="speech-error">{error}</div>
            <button
              type="button"
              className="record-again-btn"
              onClick={reset}
            >
              Try Again
            </button>
          </div>
        )}
      </div>

      {/* ── Transcript Preview ── */}
      {transcript && (
        <div className="transcript-preview">
          <span className="transcript-label">Transcript:</span>
          <p>{transcript}</p>
        </div>
      )}
    </div>
  )
}

export default SpeechRecorder