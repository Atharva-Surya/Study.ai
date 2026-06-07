import React, { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'

export default function ChatWindow({ messages = [], typing = false }) {
  const scrollRef = useRef(null)

  // Scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, typing])

  return (
    <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3">
      {messages.map((m, i) => (
        <MessageBubble key={i} message={m} />
      ))}

      {typing && (
        <div className="rounded-2xl border border-[#333333] bg-[#101010] px-4 py-3 text-sm text-[#b8ac6d]">
          Assistant is typing...
        </div>
      )}
    </div>
  )
}
