import React, { useState } from 'react'

export default function Sidebar({ chats = [], selectedChatId, onNewChat, onSelectChat, onUploadClick, onLogout }) {
  const [isCollapsed, setIsCollapsed] = useState(false)

  return (
    <aside className={`${isCollapsed ? 'w-20' : 'w-72'} bg-[#090909] border-r border-[#333333] flex flex-col gap-5 p-5 text-[#fff7b3] transition-all duration-300`}>
      {/* Header with Logo */}
      <div className="flex items-center justify-between gap-3 pb-4 border-b border-[#333333]">
        <div className={`flex items-center gap-3 ${isCollapsed ? 'hidden' : 'flex'}`}>
          <img src="/logo.svg" alt="Study.ai Logo" className="h-10 w-10 rounded-lg" />
          <div className="flex-1">
            <div className="text-lg font-bold text-[#fff7b3]">Study.ai</div>
            <div className="text-xs text-[#7b7046]">Study space</div>
          </div>
        </div>
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="rounded-lg hover:bg-[#1a1a1a] p-2 transition text-[#ffd600]"
          title={isCollapsed ? 'Expand' : 'Collapse'}
        >
          {isCollapsed ? '→' : '←'}
        </button>
      </div>

      {/* New Chat Button */}
      <button
        onClick={onNewChat}
        className="w-full rounded-xl border-2 border-[#333333] bg-[#111111] px-4 py-3 text-sm font-semibold text-[#fff7b3] hover:border-[#ffd600] hover:bg-[#1a1a1a] transition flex items-center justify-center gap-2"
      >
        <span>+</span>
        <span className={isCollapsed ? 'hidden' : 'inline'}>New Chat</span>
      </button>

      {/* Recent Chats */}
      <div className={`flex-1 overflow-y-auto space-y-2 ${isCollapsed ? 'hidden' : 'block'}`}>
        <div className="text-xs uppercase tracking-[0.3em] text-[#ffd600] font-semibold px-2">Recent</div>
        {chats.length === 0 ? (
          <div className="text-xs text-[#b8ac6d] px-2 py-3">No conversations yet.</div>
        ) : (
          chats.map((chat) => (
            <button
              key={chat.id}
              onClick={() => onSelectChat(chat.id)}
              className={`w-full rounded-xl border-2 px-4 py-3 text-left text-sm transition ${
                selectedChatId === chat.id
                  ? 'border-[#ffd600] bg-[#ffd600] text-[#050505] font-semibold'
                  : 'border-[#333333] bg-[#0b0b0b] text-[#fff7b3] hover:border-[#ffd600] hover:bg-[#151515]'
              }`}
            >
              <div className="font-medium truncate">{chat.title}</div>
              <div className={`mt-1 text-xs truncate ${selectedChatId === chat.id ? 'text-[#3b3200] opacity-75' : 'text-[#7b7046]'}`}>
                {chat.lastMessage}
              </div>
            </button>
          ))
        )}
      </div>

      {/* Footer Actions */}
      <div className="space-y-2 pt-4 border-t border-[#333333]">
        <button
          onClick={onUploadClick}
          className="w-full rounded-xl border-2 border-[#333333] bg-[#111111] px-4 py-3 text-sm text-[#fff7b3] hover:border-[#ffd600] hover:bg-[#1a1a1a] transition flex items-center justify-center gap-2"
          title="Toggle PDF Panel"
        >
          <span>📄</span>
          <span className={isCollapsed ? 'hidden' : 'inline'}>PDF Panel</span>
        </button>
        <button
          onClick={onLogout}
          className="w-full rounded-xl border-2 border-[#333333] bg-[#111111] px-4 py-3 text-sm text-[#fff7b3] hover:border-[#ff9b9b] hover:text-[#ff9b9b] hover:bg-[#1a1a1a] transition flex items-center justify-center gap-2"
          title="Logout"
        >
          <span>🚪</span>
          <span className={isCollapsed ? 'hidden' : 'inline'}>Logout</span>
        </button>
      </div>
    </aside>
  )
}
