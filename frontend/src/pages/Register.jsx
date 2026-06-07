import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const auth = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      await auth.register(username.trim(), email.trim(), password)
      setSuccess('Account created successfully. Redirecting to login...')
      setTimeout(() => navigate('/login'), 1200)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  return (
    <main className="page-shell">
      <section className="auth-card">
        <div className="auth-logo">
          <img src="/logo.svg" alt="Study Assistant Logo" />
          <div>
            <h1 style={{ marginBottom: 0 }}>Create account</h1>
            <p className="subtitle" style={{ marginBottom: 0 }}>Start your AI-powered study journey</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            Username
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="user"
              required
              minLength={3}
              autoFocus
              disabled={loading}
            />
          </label>

          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="user@example.com"
              required
              disabled={loading}
            />
          </label>

          <label>
            Password
            <div style={{ position: 'relative', width: '100%' }}>
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                minLength={6}
                disabled={loading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '1rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: '#b8ac6d',
                  cursor: 'pointer',
                  fontSize: '1.2rem',
                }}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
          </label>

          {error && <div className="alert error">{error}</div>}
          {success && <div className="alert success">{success}</div>}

          <button type="submit" className="primary-button" disabled={loading}>
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>

        <p className="form-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </section>
    </main>
  )
}
