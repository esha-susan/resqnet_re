// frontend/src/App.jsx
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import Incidents from './pages/Incidents'
import IncidentView from './pages/IncidentView'
import Resources from './pages/Resources'
import Reports from './pages/Reports'              // ← NEW
import Home from './pages/Home'

function ProtectedRoute({ children }) {
  const { user } = useAuth()
  return user ? children : <Navigate to="/login" replace />
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/dashboard" element={
        <ProtectedRoute><Dashboard /></ProtectedRoute>
      }/>
      <Route path="/incidents" element={
        <ProtectedRoute><Incidents /></ProtectedRoute>
      }/>
      <Route path="/incidents/:id" element={
        <ProtectedRoute><IncidentView /></ProtectedRoute>
      }/>
      <Route path="/resources" element={
        <ProtectedRoute><Resources /></ProtectedRoute>
      }/>
      <Route path="/reports" element={
        <ProtectedRoute><Reports /></ProtectedRoute>
      }/>
    </Routes>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}

export default App