import React from 'react'

export default function FlashcardCard({
  card,
  index,
  total,
  showAnswer,
  onToggleAnswer,
  onPrev,
  onNext,
  hasPrev,
  hasNext,
}) {
  return (
    <div className="rounded-2xl border border-[#333333] bg-[#111111] p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between text-sm text-[#b8ac6d] mb-4">
        <span>Flashcard {index + 1} of {total}</span>
        <button
          type="button"
          onClick={onToggleAnswer}
          className="rounded-xl border border-[#333333] px-4 py-2 text-[#fff7b3] hover:border-[#ffd600] transition"
        >
          {showAnswer ? 'Hide answer' : 'Show answer'}
        </button>
      </div>

      <div className="text-base font-semibold text-[#fff7b3] mb-4">{card.question}</div>
      {showAnswer && (
        <div className="rounded-xl border border-[#333333] bg-[#0b0b0b] p-4 text-[#fff7b3] leading-7">
          {card.answer}
        </div>
      )}

      <div className="mt-5 flex gap-2">
        <button
          type="button"
          onClick={onPrev}
          disabled={!hasPrev}
          className="flex-1 rounded-xl border border-[#333333] bg-[#101010] px-4 py-3 text-sm text-[#fff7b3] disabled:cursor-not-allowed disabled:opacity-50 hover:border-[#ffd600] transition"
        >
          Previous
        </button>
        <button
          type="button"
          onClick={onNext}
          disabled={!hasNext}
          className="flex-1 rounded-xl border border-[#333333] bg-[#101010] px-4 py-3 text-sm text-[#fff7b3] disabled:cursor-not-allowed disabled:opacity-50 hover:border-[#ffd600] transition"
        >
          Next
        </button>
      </div>
    </div>
  )
}
