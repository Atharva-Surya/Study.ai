import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Profile() {
  const auth = useAuth()
  const navigate = useNavigate()
  const [streakData, setStreakData] = useState({})

  useEffect(() => {
    if (!auth.isAuthenticated && !auth.loading) {
      navigate('/login')
    }
    // Initialize streak data from localStorage
    const saved = localStorage.getItem('streak_data')
    setStreakData(saved ? JSON.parse(saved) : {})
  }, [auth.isAuthenticated, auth.loading, navigate])

  const handleBackToDashboard = () => {
    navigate('/dashboard')
  }

  // Get current month and year
  const now = new Date()
  const currentMonth = now.getMonth()
  const currentYear = now.getFullYear()
  const monthName = new Date(currentYear, currentMonth).toLocaleString('default', { month: 'long', year: 'numeric' })

  // Get days in month
  const firstDay = new Date(currentYear, currentMonth, 1).getDay()
  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate()
  const days = []

  // Add empty cells for days before month starts
  for (let i = 0; i < firstDay; i++) {
    days.push(null)
  }

  // Add days of month
  for (let i = 1; i <= daysInMonth; i++) {
    days.push(i)
  }

  // Check if a day has activity
  const hasActivity = (day) => {
    if (!day) return false
    const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    return streakData[dateStr] === true
  }

  // Calculate current streak
  const calculateStreak = () => {
    let streak = 0
    let date = new Date(currentYear, currentMonth, currentDate)
    while (true) {
      const dateStr = date.toISOString().split('T')[0]
      if (streakData[dateStr] === true) {
        streak++
        date.setDate(date.getDate() - 1)
      } else {
        break
      }
    }
    return streak
  }

  const currentDate = now.getDate()
  const currentStreak = calculateStreak()

  return (
    <div className="min-h-screen bg-[#0b0b0b] text-[#fff7b3]">
      {/* Header */}
      <div className="w-full flex items-center justify-between p-6 border-b border-[#333333] bg-[#0b0b0b]">
        <div>
          <div className="text-xs uppercase tracking-[0.3em] text-[#ffd600]">User Profile</div>
          <h1 className="text-3xl font-semibold text-[#fff7b3]">My Study Profile</h1>
        </div>
        <button
          onClick={handleBackToDashboard}
          className="rounded-lg border border-[#ffd600] bg-[#1a1a1a] px-6 py-2 text-[#ffd600] hover:bg-[#2a2a2a] transition-colors"
        >
          Back to Dashboard
        </button>
      </div>

      {/* Main Content */}
      <div className="p-8">
        {/* User Info Card */}
        <div className="mb-8 rounded-2xl border border-[#333333] bg-[#111111] p-6">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
            <div>
              <div className="text-sm text-[#b8ac6d] mb-2">Username</div>
              <div className="text-xl font-semibold text-[#ffd600]">{auth.user?.username ?? 'User'}</div>
            </div>
            <div>
              <div className="text-sm text-[#b8ac6d] mb-2">Email</div>
              <div className="text-lg text-[#fff7b3]">{auth.user?.email ?? 'No email'}</div>
            </div>
            <div>
              <div className="text-sm text-[#b8ac6d] mb-2">Member Since</div>
              <div className="text-lg text-[#fff7b3]">
                {auth.user?.created_at ? new Date(auth.user.created_at).toLocaleDateString() : 'N/A'}
              </div>
            </div>
          </div>
        </div>

        {/* Streak Info */}
        <div className="mb-8 rounded-2xl border border-[#333333] bg-[#111111] p-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="text-5xl">🔥</div>
            <div>
              <div className="text-sm text-[#b8ac6d]">Current Streak</div>
              <div className="text-4xl font-bold text-[#ffd600]">{currentStreak} days</div>
            </div>
          </div>
          <p className="text-sm text-[#b8ac6d]">Keep studying to maintain your streak!</p>
        </div>

        {/* Streak Calendar */}
        <div className="rounded-2xl border border-[#333333] bg-[#111111] p-6">
          <h2 className="text-2xl font-semibold text-[#ffd600] mb-6">Study Calendar - {monthName}</h2>
          
          {/* Weekday headers */}
          <div className="grid grid-cols-7 gap-2 mb-4">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
              <div key={day} className="text-center text-sm text-[#b8ac6d] font-semibold py-2">
                {day}
              </div>
            ))}
          </div>

          {/* Days grid */}
          <div className="grid grid-cols-7 gap-2">
            {days.map((day, idx) => {
              if (day === null) {
                return <div key={`empty-${idx}`} className="aspect-square"></div>
              }

              const isActive = hasActivity(day)
              const isToday = day === currentDate
              const isUpcoming = day > currentDate

              return (
                <div
                  key={day}
                  className={`aspect-square flex items-center justify-center rounded-lg font-semibold text-sm transition-all ${
                    isActive
                      ? 'bg-[#ffd600] text-[#0b0b0b]'
                      : isToday
                      ? 'border-2 border-[#ffd600] bg-[#1a1a1a] text-[#fff7b3]'
                      : isUpcoming
                      ? 'bg-[#0a0a0a] text-[#666666] border border-[#333333]'
                      : 'bg-[#1a1a1a] text-[#b8ac6d] border border-[#333333]'
                  }`}
                >
                  {day}
                </div>
              )
            })}
          </div>

          {/* Legend */}
          <div className="mt-6 grid grid-cols-1 gap-3 md:grid-cols-3">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#ffd600] rounded"></div>
              <span className="text-sm text-[#b8ac6d]">Active Day</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-[#ffd600] bg-[#1a1a1a] rounded"></div>
              <span className="text-sm text-[#b8ac6d]">Today</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#1a1a1a] border border-[#333333] rounded"></div>
              <span className="text-sm text-[#b8ac6d]">Inactive Day</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
