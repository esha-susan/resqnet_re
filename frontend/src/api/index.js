// frontend/src/api/index.js
// Updated: all API calls now attach the JWT token in the Authorization header
// so Flask can verify who is making the request.

import axios from 'axios'
import { supabase } from './supabaseClient'

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

// Axios interceptor: automatically adds auth token to EVERY request
// This means Person A never has to manually add headers — it's automatic
API.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession()
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`
  }
  return config
})

// ── Health ──
export const checkHealth = async () => {
  const response = await API.get('/api/health')
  return response.data
}

// ── Auth ──
export const getProfile = async () => {
  const response = await API.get('/api/auth/profile')
  return response.data
}