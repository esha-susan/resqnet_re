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
      <div className="navbar-brand">🚨 ResQNet</div>
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