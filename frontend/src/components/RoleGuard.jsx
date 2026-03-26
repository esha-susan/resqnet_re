// frontend/src/components/RoleGuard.jsx
// Wraps any route/component and only renders it if the
// current user has one of the allowed roles.
// Redirects to /dashboard with an "access denied" message otherwise.

import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/**
 * Usage examples:
 *
 * // Only admins can see this page
 * <RoleGuard allowed={['admin']}>
 *   <AdminPanel />
 * </RoleGuard>
 *
 * // Police and admins can see this page
 * <RoleGuard allowed={['admin', 'police']}>
 *   <PoliceIncidents />
 * </RoleGuard>
 */
function RoleGuard({ allowed, children }) {
  const { userRole } = useAuth()

  // If the user's role is in the allowed list → render children
  if (allowed.includes(userRole)) {
    return children
  }

  // Otherwise redirect to dashboard with a denial flag in state
  return <Navigate to="/dashboard" state={{ accessDenied: true }} replace />
}

export default RoleGuard