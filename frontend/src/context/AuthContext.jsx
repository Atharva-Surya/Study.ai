import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const AuthContext = createContext(null)

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8004/api/v1'

async function loginUser(identifier, password) {
  const formData = new URLSearchParams()
  formData.append('username', identifier)
  formData.append('password', password)

  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new Error(payload?.detail || 'Login failed')
  }

  return response.json()
}

async function registerUser(username, email, password) {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, email, password }),
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new Error(payload?.detail || 'Registration failed')
  }

  return response.json()
}

async function fetchProfile(token) {
  const response = await fetch(`${API_BASE}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error('Unable to load profile')
  }

  return response.json()
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('study_app_token'))
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(token))

  useEffect(() => {
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }

    let cancelled = false
    setLoading(true)

    fetchProfile(token)
      .then((profile) => {
        if (!cancelled) {
          setUser(profile)
        }
      })
      .catch(() => {
        localStorage.removeItem('study_app_token')
        setToken(null)
        setUser(null)
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [token])

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      isAuthenticated: Boolean(token),
      login: async (identifier, password) => {
        const data = await loginUser(identifier, password)
        localStorage.setItem('study_app_token', data.access_token)
        setToken(data.access_token)
        return data
      },
      register: async (username, email, password) => {
        return registerUser(username, email, password)
      },
      logout: () => {
        localStorage.removeItem('study_app_token')
        setToken(null)
        setUser(null)
      },
    }),
    [token, user, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
