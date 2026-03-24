// frontend/src/components/Navbar.jsx
// Top navigation bar shown on all protected pages.
// Shows the app name and a logout button.

import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import '../styles/auth.css'

function Navbar() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await signOut()
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand logo-container">
        <div className="logo-icon">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
          </svg>
        </div>
        ResQNet
      </div>
      <div className="navbar-right">
        <span className="navbar-user">{user?.email}</span>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </div>
    </nav>
  )
}

export default Navbar