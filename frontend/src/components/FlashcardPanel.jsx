import React from 'react'
import FlashcardCard from './FlashcardCard'

export default function FlashcardPanel({
  topic,
  details,
  setTopic,
  setDetails,
  onGenerate,
  loading,
  error,
  flashcards,
  activeIndex,
  showAnswer,
  onToggleAnswer,
  onPrevCard,
  onNextCard,
}) {
  const card = flashcards[activeIndex]

  return (
    <section className="rounded-2xl border border-[#333333] bg-[#111111] p-5 text-[#fff7b3]">
      <div className="mb-4">
        <div className="text-sm uppercase tracking-[0.24em] text-[#ffd600]">Flashcards</div>
        <h2 className="mt-2 text-2xl font-semibold text-[#fff7b3]">Generate Study Cards</h2>
        <p className="mt-2 text-sm leading-6 text-[#b8ac6d]">
          Enter a topic and get simple, review-ready flashcards you can cycle through.
        </p>
      </div>

      <div className="space-y-3 mb-4">
        <label className="block text-sm text-[#d1c46b]">
          Topic
          <input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Example: Cloud Computing"
            className="mt-2 w-full rounded-xl border border-[#333333] bg-[#101010] px-4 py-3 text-sm text-[#fff7b3] outline-none focus:border-[#ffd600]"
          />
        </label>
        <label className="block text-sm text-[#d1c46b]">
          Details (optional)
          <input
            value={details}
            onChange={(e) => setDetails(e.target.value)}
            placeholder="Add a short description or course context"
            className="mt-2 w-full rounded-xl border border-[#333333] bg-[#101010] px-4 py-3 text-sm text-[#fff7b3] outline-none focus:border-[#ffd600]"
          />
        </label>
      </div>

      {error && <div className="rounded-xl border border-[#7f1d1d] bg-[#220606] p-3 text-sm text-[#ffb3b3] mb-4">{error}</div>}

      <button
        type="button"
        onClick={onGenerate}
        disabled={loading || !topic.trim()}
        className="w-full rounded-xl border border-[#b08c00] bg-[#ffd600] px-4 py-3 text-sm font-semibold text-[#111111] transition hover:bg-[#e6c000] disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? 'Generating flashcards...' : 'Generate Flashcards'}
      </button>

      <div className="mt-5 space-y-4">
        {flashcards.length > 0 ? (
          <FlashcardCard
            card={card}
            index={activeIndex}
            total={flashcards.length}
            showAnswer={showAnswer}
            onToggleAnswer={onToggleAnswer}
            onPrev={onPrevCard}
            onNext={onNextCard}
            hasPrev={activeIndex > 0}
            hasNext={activeIndex < flashcards.length - 1}
          />
        ) : (
          <div className="rounded-2xl border border-[#333333] bg-[#0b0b0b] p-5 text-sm text-[#b8ac6d]">
            Generate a set of flashcards to preview them here.
          </div>
        )}
      </div>
    </section>
  )
}
