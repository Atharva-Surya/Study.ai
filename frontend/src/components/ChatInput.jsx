import React, { useState } from 'react'

export default function ChatInput({ onSend, disabled }) {
  const [text, setText] = useState('')

  const submit = async (e) => {
    if (e) e.preventDefault()
    const trimmed = text.trim()
    if (!trimmed) return
    setText('')
    await onSend(trimmed)
  }

  return (
    <form onSubmit={submit} className="p-5 border-t border-[#333333] bg-[#0b0b0b] flex flex-col gap-3 sm:flex-row items-center">
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        className="flex-1 rounded-xl border border-[#333333] bg-[#101010] px-4 py-3 text-sm text-[#fff7b3] placeholder:text-[#7d7d7d] outline-none focus:border-[#ffd600]"
        placeholder="Type your message and press Enter"
        disabled={disabled}
      />
      <button
        type="submit"
        disabled={disabled}
        className="w-full rounded-xl border border-[#b08c00] bg-[#ffd600] px-4 py-3 text-sm font-semibold text-[#111111] transition hover:bg-[#e6c000] disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
      >
        {disabled ? 'Sending...' : 'Send'}
      </button>
    </form>
  )
}
