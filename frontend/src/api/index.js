// frontend/src/api/index.js
import axios from 'axios'
import { supabase } from './supabaseClient'

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

API.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession()
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`
  }
  return config
})

// ── Health ──
export const checkHealth = async () => {
  const res = await API.get('/api/health')
  return res.data
}

// ── Auth ──
export const getProfile = async () => {
  const res = await API.get('/api/auth/profile')
  return res.data
}

// ── Incidents ──
export const fetchIncidents = async () => {
  const res = await API.get('/api/incidents')
  return res.data
}

export const createIncident = async (incidentData) => {
  const res = await API.post('/api/incidents', incidentData)
  return res.data
}

export const updateIncidentStatus = async (id, status) => {
  const res = await API.patch(`/api/incidents/${id}/status`, { status })
  return res.data
}

export const updateIncidentPriority = async (id, priority) => {
  const res = await API.patch(`/api/incidents/${id}/priority`, { priority })
  return res.data
}

export const closeIncident = async (id) => {
  const res = await API.post(`/api/incidents/${id}/close`)
  return res.data
}

export const fetchIncidentById = async (id) => {
  const res = await API.get(`/api/incidents/${id}`)
  return res.data
}

// ── Speech ──
export const transcribeAudio = async (audioBlob, incidentId = null) => {
  const formData = new FormData()
  formData.append('audio', audioBlob, 'recording.webm')
  if (incidentId) formData.append('incident_id', incidentId)
  const res = await API.post('/api/speech/transcribe', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return res.data
}

// ── Resources ──
export const fetchResources = async (status = null) => {
  const url = status
    ? `/api/resources?status=${status}`
    : '/api/resources'
  const res = await API.get(url)
  return res.data
}

export const fetchIncidentResources = async (incidentId) => {
  const res = await API.get(`/api/resources/incident/${incidentId}`)
  return res.data
}

export const fetchAllIncidentResources = async (incidentId) => {
  const res = await API.get(`/api/resources/incident/${incidentId}/all`)
  return res.data
}

export const releaseResource = async (resourceId, incidentId) => {
  const res = await API.post('/api/resources/release', {
    resource_id: resourceId,
    incident_id: incidentId
  })
  return res.data
}

export const releaseAllResources = async (incidentId) => {
  const res = await API.post(`/api/resources/release-all/${incidentId}`)
  return res.data
}

// ── Twilio ──
export const fetchCallLogs = async (incidentId) => {
  const res = await API.get(`/api/twilio/call-logs/${incidentId}`)
  return res.data
}