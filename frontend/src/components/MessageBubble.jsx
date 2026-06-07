import React from 'react'

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} my-3`}>
      <div className={`max-w-[85%] rounded-2xl border px-4 py-3 text-sm leading-7 ${isUser ? 'border-[#b08c00] bg-[#ffd600] text-[#111111]' : 'border-[#333333] bg-[#101010] text-[#fff7b3]'}`}>
        {message.content}
      </div>
    </div>
  )
}
