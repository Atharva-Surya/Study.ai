import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'
import ChatWindow from '../components/ChatWindow'
import ChatInput from '../components/ChatInput'
import { useAuth } from '../context/AuthContext'

export default function RAG() {
  const auth = useAuth()
  const navigate = useNavigate()

  const [uploadedPdfName, setUploadedPdfName] = useState('')
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Welcome to the RAG System. Upload a PDF and ask questions about its content.' }
  ])
  const [chatLoading, setChatLoading] = useState(false)
  const [typing, setTyping] = useState(false)
  const [chatError, setChatError] = useState('')
  const [uploadError, setUploadError] = useState('')
  const [uploading, setUploading] = useState(false)

  const handlePdfUpload = async (event) => {
    const files = event.target.files
    if (!files || files.length === 0) return

    const file = files[0]
    setUploading(true)
    setUploadError('')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8004/api/v1'
      const response = await fetch(`${API_BASE}/rag/upload`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${auth.token}`,
        },
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData?.detail || 'Upload failed')
      }

      const data = await response.json()
      setUploadedPdfName(file.name)
      setMessages([
        { role: 'assistant', content: `✓ Successfully uploaded "${file.name}". Now I can answer questions about this document.` }
      ])
    } catch (err) {
      console.error('Upload error', err)
      setUploadError(err.message || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const handleSend = async (text) => {
    if (!uploadedPdfName) {
      setChatError('Please upload a PDF first.')
      return
    }

    const userMsg = { role: 'user', content: text }
    const nextMessages = [...messages, userMsg]
    setMessages(nextMessages)
    setChatError('')

    setChatLoading(true)
    setTyping(true)

    try {
      const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8004/api/v1'
      const response = await fetch(`${API_BASE}/rag/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${auth.token}`,
        },
        body: JSON.stringify({ question: text }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData?.detail || 'Failed to get RAG response')
      }

      const data = await response.json()
      const assistant = {
        role: 'assistant',
        content: data.answer || 'No answer available.'
      }
      setMessages((current) => [...current, assistant])
    } catch (err) {
      console.error('RAG chat error', err)
      setChatError(err.message || 'An error occurred. Please try again.')
    } finally {
      setChatLoading(false)
      setTyping(false)
    }
  }

  return (
    <div className="min-h-screen flex bg-[#050505] text-[#fff7b3]">
      <Sidebar
        chats={[]}
        selectedChatId=""
        onNewChat={() => {}}
        onSelectChat={() => {}}
        onUploadClick={() => {}}
        onLogout={() => {
          auth.logout()
          navigate('/login')
        }}
      />

      <div className="flex-1 flex flex-col">
        <Navbar user={auth.user} />

        <main className="flex-1 grid gap-4 p-4 lg:p-6 lg:grid-cols-[1.7fr_1fr]">
          <section className="flex flex-col rounded-2xl border border-[#333333] bg-[#111111] overflow-hidden">
            <div className="flex flex-col gap-2 border-b border-[#333333] bg-[#0b0b0b] px-6 py-5">
              <div className="text-xs uppercase tracking-[0.3em] text-[#ffd600]">RAG System</div>
              <div className="text-2xl font-semibold text-[#fff7b3]">Document Q&A</div>
              <p className="max-w-2xl text-sm text-[#b8ac6d]">Upload a PDF and ask questions about its content.</p>
            </div>

            <div className="flex-1 overflow-hidden">
              <ChatWindow messages={messages} typing={typing} />
            </div>

            {chatError && (
              <div className="bg-[#220606] border-t border-[#333333] px-6 py-4 text-sm text-[#ffb3b3]">{chatError}</div>
            )}

            <ChatInput onSend={handleSend} disabled={chatLoading || !uploadedPdfName} />
          </section>

          <div className="space-y-4">
            <div className="rounded-2xl border border-[#333333] bg-[#111111] p-6 flex flex-col gap-4">
              <div className="flex flex-col gap-2 border-b border-[#333333] pb-4">
                <div className="text-xs uppercase tracking-[0.3em] text-[#ffd600]">PDF Upload</div>
                <div className="text-lg font-semibold text-[#fff7b3]">Upload Document</div>
              </div>

              <div className="flex flex-col gap-4">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handlePdfUpload}
                  disabled={uploading}
                  className="block w-full text-sm text-[#b8ac6d] file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-[#ffd600] file:text-[#050505] hover:file:bg-[#ffed4e] cursor-pointer disabled:opacity-50"
                />

                {uploading && (
                  <div className="rounded-lg border border-[#333333] bg-[#0b0b0b] p-4 text-sm text-[#ffd600] animate-pulse">
                    Uploading and indexing PDF...
                  </div>
                )}

                {uploadError && (
                  <div className="rounded-lg border border-[#ff6b6b] bg-[#220606] p-4 text-sm text-[#ffb3b3]">
                    {uploadError}
                  </div>
                )}

                {uploadedPdfName && !uploadError && (
                  <div className="rounded-lg border border-[#333333] bg-[#0b0b0b] p-4">
                    <div className="text-xs uppercase tracking-[0.2em] text-[#ffd600] mb-2">✓ Uploaded PDF</div>
                    <div className="text-sm text-[#fff7b3] break-words">{uploadedPdfName}</div>
                  </div>
                )}

                {!uploadedPdfName && !uploadError && (
                  <div className="rounded-lg border border-[#333333] bg-[#0b0b0b] p-4">
                    <div className="text-xs uppercase tracking-[0.2em] text-[#b8ac6d] mb-2">No PDF Uploaded</div>
                    <div className="text-sm text-[#b8ac6d]">Select a PDF file to begin.</div>
                  </div>
                )}
              </div>

              <button
                onClick={() => navigate('/dashboard')}
                className="w-full mt-4 rounded-lg bg-[#ffd600] text-[#050505] font-semibold py-2 hover:bg-[#ffed4e] transition"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
