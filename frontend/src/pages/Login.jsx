import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const auth = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      await auth.login(identifier.trim(), password)
      navigate('/dashboard')
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
            <h1 style={{ marginBottom: 0 }}>Welcome back</h1>
            <p className="subtitle" style={{ marginBottom: 0 }}>Sign in to your study space</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            Username or Email
            <input
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              placeholder="user or user@example.com"
              required
              autoFocus
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

          <button type="submit" className="primary-button" disabled={loading}>
            {loading ? (
              <span>Signing in...</span>
            ) : (
              'Sign in'
            )}
          </button>
        </form>

        <p className="form-footer">
          New here? <Link to="/register">Create an account</Link>
        </p>
      </section>
    </main>
  )
}
