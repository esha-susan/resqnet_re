// frontend/src/pages/Signup.jsx
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import '../styles/auth.css'
import '../styles/signup-roles.css'

const ROLES = [
  { value: 'admin',     label: 'Admin',         icon: '', desc: 'Full system access'          },
  { value: 'police',    label: 'Police',         icon: '', desc: 'Law enforcement response'    },
  { value: 'ambulance', label: 'Ambulance',      icon: '', desc: 'Medical emergency response'  },
  { value: 'fireforce',label: 'Fire & Rescue',  icon: '', desc: 'Fire suppression & rescue'   },
  { value: 'doctor',    label: 'Doctor',         icon: '', desc: 'Medical team on-site'        },
]

function Signup() {
  const { signUp } = useAuth()
  const navigate   = useNavigate()

  const [fullName, setFullName] = useState('')
  const [email,    setEmail]    = useState('')
  const [password, setPassword] = useState('')
  const [confirm,  setConfirm]  = useState('')
  const [role,     setRole]     = useState('')
  const [error,    setError]    = useState('')
  const [message,  setMessage]  = useState('')
  const [loading,  setLoading]  = useState(false)

  const handleSignup = async (e) => {
    e.preventDefault()
    setError('')

    if (!role)             return setError('Please select your role.')
    if (!fullName.trim())  return setError('Please enter your full name.')
    if (password !== confirm) return setError('Passwords do not match.')
    if (password.length < 6)  return setError('Password must be at least 6 characters.')

    setLoading(true)
    const { error } = await signUp(email, password, fullName.trim(), role)

    if (error) {
      setError(error.message)
    } else {
      setMessage('Account created! Check your email to confirm, then log in.')
    }
    setLoading(false)
  }

  return (
    <div className="auth-container">
      <div className="auth-card signup-card">

        <div className="auth-header">
          <h1>ResQNet<span className="auth-dot"></span></h1>
          <p>Create your account</p>
        </div>

        {error   && <div className="auth-error">{error}</div>}
        {message && <div className="auth-success">{message}</div>}

        <form onSubmit={handleSignup} className="auth-form">

          <div className="form-group">
            <label>Full Name</label>
            <input
              type="text"
              placeholder="John Smith"
              value={fullName}
              onChange={e => setFullName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Your Role</label>
            <div className="role-grid">
              {ROLES.map(r => (
                <button
                  key={r.value}
                  type="button"
                  className={`role-card ${role === r.value ? 'selected' : ''}`}
                  onClick={() => setRole(r.value)}
                >
                  <span className="role-icon">{r.icon}</span>
                  <span className="role-label">{r.label}</span>
                  <span className="role-desc">{r.desc}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Min. 6 characters"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Confirm Password</label>
            <input
              type="password"
              placeholder="••••••••"
              value={confirm}
              onChange={e => setConfirm(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="auth-btn" disabled={loading}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>

        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>

      </div>
    </div>
  )
}

export default Signup