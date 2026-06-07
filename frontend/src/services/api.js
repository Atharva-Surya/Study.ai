// services/api.js
// Central axios instance and API helpers.
import axios from 'axios'
import { getToken } from '../utils/auth'

// Base URL for API calls. Use Vite env override when provided.
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8004/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach Authorization header to each request when token exists.
api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Helper for chat POST. The backend expects messages payload.
export async function sendChat(messages) {
  try {
    console.debug('[API] sendChat payload:', messages)
    const res = await api.post('/chat', { messages })
    console.debug('[API] sendChat response:', res.data)
    return res.data
  } catch (error) {
    console.error('[API] sendChat error:', error)
    throw error
  }
}

export async function generateFlashcards(topic, details = '') {
  try {
    console.debug('[API] generateFlashcards topic:', topic)
    const res = await api.post('/generate-flashcards', { topic, details })
    return res.data
  } catch (error) {
    console.error('[API] generateFlashcards error:', error)
    throw error
  }
}

export async function generateQuiz(topic, details = '') {
  try {
    console.debug('[API] generateQuiz topic:', topic)
    const res = await api.post('/generate-quiz', { topic, details })
    return res.data
  } catch (error) {
    console.error('[API] generateQuiz error:', error)
    throw error
  }
}

export default api
