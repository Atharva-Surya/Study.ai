import React from 'react'
import { useNavigate } from 'react-router-dom'

export default function Navbar({ user }) {
  const navigate = useNavigate()

  const handleProfileClick = () => {
    navigate('/profile')
  }

  return (
    <div className="w-full flex flex-col gap-4 px-6 py-4 border-b border-[#333333] bg-[#0b0b0b] text-[#fff7b3] shadow-sm">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        {/* Left Section: Logo + Title */}
        <div className="flex items-center gap-4 flex-1">
          <img src="/logo.svg" alt="Study Assistant" className="h-12 w-12 rounded-lg" />
          <div>
            <div className="text-xs uppercase tracking-[0.3em] text-[#ffd600] font-semibold">AI Study Assistant</div>
            <h2 className="text-2xl font-bold text-[#fff7b3]">Study Dashboard</h2>
          </div>
        </div>

        {/* Right Section: Buttons */}
        <div className="flex items-center gap-3 md:gap-4">
          {/* RAG System Button */}
          <button
            onClick={() => navigate('/rag')}
            className="group relative px-5 py-2.5 rounded-lg bg-gradient-to-r from-[#ffd600] to-[#ffed4e] text-[#050505] font-bold text-xs uppercase tracking-[0.08em] shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 active:translate-y-0 flex items-center gap-2 whitespace-nowrap"
          >
            <span className="text-lg">📄</span>
            <span className="hidden sm:inline">RAG</span>
          </button>

          {/* Profile Button */}
          <button
            onClick={handleProfileClick}
            className="group px-4 py-2.5 rounded-lg border-2 border-[#ffd600] bg-transparent hover:bg-[#ffd600] hover:bg-opacity-15 font-semibold text-xs transition-all duration-300 transform hover:-translate-y-1 active:translate-y-0 flex items-center gap-2"
          >
            <span className="text-lg">👤</span>
            <span className="text-[#fff7b3] group-hover:text-[#ffd600] transition-colors hidden sm:inline max-w-[120px] truncate">
              {user?.username ?? 'Profile'}
            </span>
          </button>
        </div>
      </div>

      {/* Subtitle */}
      <div className="text-xs text-[#b8ac6d] font-medium">A clean, minimal workspace for chat, flashcards, and quiz practice.</div>
    </div>
  )
}
