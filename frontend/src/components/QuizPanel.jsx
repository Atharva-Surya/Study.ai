import React from 'react'
import QuizQuestion from './QuizQuestion'

export default function QuizPanel({
  topic,
  details,
  setTopic,
  setDetails,
  onGenerate,
  loading,
  error,
  questions,
  activeIndex,
  selectedOption,
  onSelectOption,
  onNextQuestion,
  completed,
  score,
  onRestart,
}) {
  const currentQuestion = questions[activeIndex]

  return (
    <section className="rounded-2xl border border-[#333333] bg-[#111111] p-5 text-[#fff7b3]">
      <div className="mb-4">
        <div className="text-sm uppercase tracking-[0.24em] text-[#ffd600]">Quiz</div>
        <h2 className="mt-2 text-2xl font-semibold text-[#fff7b3]">Generate a Practice Quiz</h2>
        <p className="mt-2 text-sm leading-6 text-[#b8ac6d]">
          Create a quick MCQ quiz and answer each question to see your score.
        </p>
      </div>

      <div className="space-y-3 mb-4">
        <label className="block text-sm text-[#d1c46b]">
          Topic
          <input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Example: HTML, CSS, JavaScript"
            className="mt-2 w-full rounded-xl border border-[#333333] bg-[#101010] px-4 py-3 text-sm text-[#fff7b3] outline-none focus:border-[#ffd600]"
          />
        </label>
        <label className="block text-sm text-[#d1c46b]">
          Details (optional)
          <input
            value={details}
            onChange={(e) => setDetails(e.target.value)}
            placeholder="Short description or context"
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
        {loading ? 'Generating quiz...' : 'Generate Quiz'}
      </button>

      <div className="mt-5 space-y-4">
        {questions.length > 0 ? (
          <div className="space-y-4">
            {completed ? (
              <div className="rounded-2xl border border-[#333333] bg-[#0b0b0b] p-5 text-[#fff7b3]">
                <div className="text-lg font-semibold text-[#fff7b3]">Quiz completed</div>
                <div className="mt-3 text-sm text-[#b8ac6d]">Your score: <span className="font-semibold text-[#fff7b3]">{score}/{questions.length}</span></div>
                <button
                  type="button"
                  onClick={onRestart}
                  className="mt-5 rounded-xl border border-[#b08c00] bg-[#ffd600] px-4 py-3 text-sm font-semibold text-[#111111] hover:bg-[#e6c000] transition"
                >
                  Restart Quiz
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="text-sm uppercase tracking-[0.24em] text-[#ffd600]">
                  Question {activeIndex + 1} of {questions.length}
                </div>
                <QuizQuestion
                  question={currentQuestion.question}
                  options={currentQuestion.options}
                  selectedOption={selectedOption}
                  onSelect={onSelectOption}
                />
                <button
                  type="button"
                  onClick={onNextQuestion}
                  className="w-full rounded-xl border border-[#b08c00] bg-[#ffd600] px-4 py-3 text-sm font-semibold text-[#111111] hover:bg-[#e6c000] transition"
                >
                  {activeIndex === questions.length - 1 ? 'Finish Quiz' : 'Next Question'}
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="rounded-2xl border border-[#333333] bg-[#0b0b0b] p-5 text-sm text-[#b8ac6d]">
            Generate a quiz to answer practice questions here.
          </div>
        )}
      </div>
    </section>
  )
}
