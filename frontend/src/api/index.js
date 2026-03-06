// frontend/src/api/index.js
import axios from 'axios'
import { supabase } from './supabaseClient'

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

// Auto-attach JWT token to every request
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