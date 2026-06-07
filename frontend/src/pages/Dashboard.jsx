import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'
import ChatWindow from '../components/ChatWindow'
import ChatInput from '../components/ChatInput'
import UploadSection from '../components/UploadSection'
import FlashcardPanel from '../components/FlashcardPanel'
import QuizPanel from '../components/QuizPanel'
import { sendChat, generateFlashcards, generateQuiz } from '../services/api'

export default function Dashboard() {
  const auth = useAuth()
  const navigate = useNavigate()

  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Welcome to the Gemini Study Assistant. Ask a question to start your session.' }
  ])
  const [chatLoading, setChatLoading] = useState(false)
  const [typing, setTyping] = useState(false)
  const [chatError, setChatError] = useState('')

  const [chats, setChats] = useState([
    { id: 'default', title: 'General Study', lastMessage: 'Welcome to your AI study space.' }
  ])
  const [selectedChatId, setSelectedChatId] = useState('default')

  const [flashcardTopic, setFlashcardTopic] = useState('')
  const [flashcardDetails, setFlashcardDetails] = useState('')
  const [flashcards, setFlashcards] = useState([])
  const [activeFlashcardIndex, setActiveFlashcardIndex] = useState(0)
  const [showFlashcardAnswer, setShowFlashcardAnswer] = useState(false)
  const [flashcardLoading, setFlashcardLoading] = useState(false)
  const [flashcardError, setFlashcardError] = useState('')

  const [quizTopic, setQuizTopic] = useState('')
  const [quizDetails, setQuizDetails] = useState('')
  const [quizQuestions, setQuizQuestions] = useState([])
  const [activeQuizIndex, setActiveQuizIndex] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState({})
  const [quizCompleted, setQuizCompleted] = useState(false)
  const [quizScore, setQuizScore] = useState(null)
  const [quizLoading, setQuizLoading] = useState(false)
  const [quizError, setQuizError] = useState('')

  const [showUpload, setShowUpload] = useState(true)
  const [uploadMessage, setUploadMessage] = useState('No files uploaded yet.')

  useEffect(() => {
    if (!auth.isAuthenticated && !auth.loading) {
      navigate('/login')
    }
  }, [auth.isAuthenticated, auth.loading, navigate])

  const handleNewChat = () => {
    setMessages([{ role: 'assistant', content: 'New chat ready. Ask your question!' }])
    const newChat = {
      id: `${Date.now()}`,
      title: 'New Study Session',
      lastMessage: 'New chat started.'
    }
    setChats((prev) => [newChat, ...prev])
    setSelectedChatId(newChat.id)
    setChatError('')
  }

  const handleSelectChat = (id) => {
    setSelectedChatId(id)
    // Placeholder: chat history persistence is a future improvement.
  }

  const handleLogout = () => {
    auth.logout()
    navigate('/login')
  }

  const handleSend = async (text) => {
    const userMsg = { role: 'user', content: text }
    const nextMessages = [...messages, userMsg]
    setMessages(nextMessages)
    setChatError('')
    setChats((prev) =>
      prev.map((chat) =>
        chat.id === selectedChatId ? { ...chat, lastMessage: text } : chat
      )
    )

    setChatLoading(true)
    setTyping(true)
    try {
      const resp = await sendChat(nextMessages)
      const assistant = {
        role: 'assistant',
        content: resp?.reply ?? 'I received no answer from the assistant. Please try a different prompt.'
      }
      setMessages((current) => [...current, assistant])
    } catch (err) {
      console.error('chat error', err)
      setChatError(err?.response?.data?.detail || err.message || 'Chat request failed. Please check the console.')
      setMessages((current) => [...current, { role: 'assistant', content: 'Sorry, something went wrong. Try again.' }])
    } finally {
      setTyping(false)
      setChatLoading(false)
    }
  }

  const handleGenerateFlashcards = async () => {
    const topic = flashcardTopic.trim()
    if (!topic) {
      setFlashcardError('Please enter a topic to generate flashcards.')
      return
    }
    setFlashcardLoading(true)
    setFlashcardError('')
    setFlashcards([])

    try {
      const cards = await generateFlashcards(topic, flashcardDetails)
      if (!Array.isArray(cards) || cards.length === 0) {
        throw new Error('No flashcards were returned by the AI service.')
      }
      setFlashcards(cards)
      setActiveFlashcardIndex(0)
      setShowFlashcardAnswer(false)
    } catch (err) {
      console.error('flashcard error', err)
      setFlashcardError(err?.response?.data?.detail || err.message || 'Unable to generate flashcards.')
    } finally {
      setFlashcardLoading(false)
    }
  }

  const handleGenerateQuiz = async () => {
    const topic = quizTopic.trim()
    if (!topic) {
      setQuizError('Please enter a topic to generate a quiz.')
      return
    }
    setQuizLoading(true)
    setQuizError('')
    setQuizQuestions([])
    setSelectedAnswers({})
    setQuizCompleted(false)
    setQuizScore(null)
    setActiveQuizIndex(0)

    try {
      const questions = await generateQuiz(topic, quizDetails)
      if (!Array.isArray(questions) || questions.length === 0) {
        throw new Error('No quiz questions were returned by the AI service.')
      }
      setQuizQuestions(questions)
    } catch (err) {
      console.error('quiz error', err)
      setQuizError(err?.response?.data?.detail || err.message || 'Unable to generate quiz.')
    } finally {
      setQuizLoading(false)
    }
  }

  const handleSelectQuizOption = (option) => {
    setSelectedAnswers((prev) => ({ ...prev, [activeQuizIndex]: option }))
    setQuizError('')
  }

  const handleNextQuiz = () => {
    if (!selectedAnswers[activeQuizIndex]) {
      setQuizError('Please select an answer before continuing.')
      return
    }

    if (activeQuizIndex >= quizQuestions.length - 1) {
      const score = quizQuestions.reduce((sum, question, index) => {
        return sum + (selectedAnswers[index] === question.correct_answer ? 1 : 0)
      }, 0)
      setQuizScore(score)
      setQuizCompleted(true)
      return
    }

    setActiveQuizIndex((prev) => prev + 1)
  }

  const handleRestartQuiz = () => {
    setQuizQuestions([])
    setSelectedAnswers({})
    setQuizCompleted(false)
    setQuizScore(null)
    setActiveQuizIndex(0)
    setQuizError('')
    setQuizTopic('')
    setQuizDetails('')
  }

  const handleUpload = (files) => {
    if (!files || files.length === 0) {
      setUploadMessage('No file selected yet.')
      return
    }
    const fileNames = Array.from(files).map((file) => file.name).join(', ')
    setUploadMessage(`Uploaded: ${fileNames}`)
  }

  return (
    <div className="min-h-screen flex bg-[#050505] text-[#fff7b3]">
      <Sidebar
        chats={chats}
        selectedChatId={selectedChatId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onUploadClick={() => setShowUpload((value) => !value)}
        onLogout={handleLogout}
      />

      <div className="flex-1 flex flex-col">
        <Navbar user={auth.user} />

        <main className="flex-1 grid gap-4 p-4 lg:p-6 lg:grid-cols-[1.7fr_1fr]">
          <section className="flex flex-col rounded-2xl border border-[#333333] bg-[#111111] overflow-hidden">
            <div className="flex flex-col gap-2 border-b border-[#333333] bg-[#0b0b0b] px-6 py-5">
              <div className="text-xs uppercase tracking-[0.3em] text-[#ffd600]">AI Chat</div>
              <div className="text-2xl font-semibold text-[#fff7b3]">Ask your study assistant</div>
              <p className="max-w-2xl text-sm text-[#b8ac6d]">Send a question and receive a concise study-focused answer.</p>
            </div>

            <div className="flex-1 overflow-hidden">
              <ChatWindow messages={messages} typing={typing} />
            </div>

            {chatError && (
              <div className="bg-[#220606] border-t border-[#333333] px-6 py-4 text-sm text-[#ffb3b3]">{chatError}</div>
            )}

            <ChatInput onSend={handleSend} disabled={chatLoading} />
          </section>

          <div className="space-y-4">
            <FlashcardPanel
              topic={flashcardTopic}
              details={flashcardDetails}
              setTopic={setFlashcardTopic}
              setDetails={setFlashcardDetails}
              onGenerate={handleGenerateFlashcards}
              loading={flashcardLoading}
              error={flashcardError}
              flashcards={flashcards}
              activeIndex={activeFlashcardIndex}
              showAnswer={showFlashcardAnswer}
              onToggleAnswer={() => setShowFlashcardAnswer((prev) => !prev)}
              onPrevCard={() => setActiveFlashcardIndex((prev) => Math.max(prev - 1, 0))}
              onNextCard={() => setActiveFlashcardIndex((prev) => Math.min(prev + 1, flashcards.length - 1))}
            />

            <QuizPanel
              topic={quizTopic}
              details={quizDetails}
              setTopic={setQuizTopic}
              setDetails={setQuizDetails}
              onGenerate={handleGenerateQuiz}
              loading={quizLoading}
              error={quizError}
              questions={quizQuestions}
              activeIndex={activeQuizIndex}
              selectedOption={selectedAnswers[activeQuizIndex]}
              onSelectOption={handleSelectQuizOption}
              onNextQuestion={handleNextQuiz}
              completed={quizCompleted}
              score={quizScore}
              onRestart={handleRestartQuiz}
            />

            {showUpload && (
              <UploadSection onUpload={handleUpload} message={uploadMessage} />
            )}

    
          </div>
        </main>
      </div>
    </div>
  )
}
