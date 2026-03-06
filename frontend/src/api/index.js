// frontend/src/api/index.js
// Central place for ALL API calls to the Flask backend.
// Person A imports functions from here — never writes fetch/axios calls inline in components.
// This makes it easy to change the base URL in one place.

import axios from 'axios'

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

// Health check — used to verify backend connection
export const checkHealth = async () => {
  const response = await API.get('/api/health')
  return response.data
}