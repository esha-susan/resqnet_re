// frontend/src/pages/Dashboard.jsx
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import '../styles/auth.css'

function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()

  return (
    <div>
      <Navbar />
      <div className="dashboard-container">
        <div className="dashboard-welcome">
          <h2>Welcome to ResQNet 🚨</h2>
          <p>Logged in as: <strong>{user?.email}</strong></p>
        </div>

        <div className="dashboard-grid">
          <div className="dash-card" onClick={() => navigate('/incidents')}>
            <span className="dash-icon">📋</span>
            <h3>Incidents</h3>
            <p>Report and manage active incidents</p>
          </div>
          <div className="dash-card" onClick={() => navigate('/resources')}>
            <span className="dash-icon">🚑</span>
            <h3>Resources</h3>
            <p>Track ambulances, fire trucks, and more</p>
          </div>
          <div className="dash-card" onClick={() => navigate('/incidents')}>
            <span className="dash-icon">🎙️</span>
            <h3>Speech Report</h3>
            <p>Submit audio disaster reports</p>
          </div>
          <div className="dash-card" onClick={() => navigate('/reports')}>
            <span className="dash-icon">📊</span>
            <h3>Reports</h3>
            <p>View closed incident reports</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard