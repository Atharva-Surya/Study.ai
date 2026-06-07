import React from 'react'

export default function QuizQuestion({ question, options, selectedOption, onSelect }) {
  return (
    <div className="rounded-2xl border border-[#333333] bg-[#111111] p-5">
      <div className="text-base font-semibold text-[#fff7b3] mb-4">{question}</div>
      <div className="space-y-3">
        {options.map((option) => {
          const selected = selectedOption === option
          return (
            <button
              key={option}
              type="button"
              onClick={() => onSelect(option)}
              className={`w-full rounded-xl border px-4 py-3 text-left text-sm transition ${selected ? 'border-[#b08c00] bg-[#ffd600] text-[#111111]' : 'border-[#333333] bg-[#101010] text-[#fff7b3] hover:border-[#ffd600]'}`}
            >
              {option}
            </button>
          )
        })}
      </div>
    </div>
  )
}
