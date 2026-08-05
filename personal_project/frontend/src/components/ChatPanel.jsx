import { useEffect, useRef, useState } from 'react'
import { askQuestion, resumeChat } from '../api/client'
import ChatMessage from './ChatMessage'
import StageInput from './StageInput'
import TypingIndicator from './TypingIndicator'

export default function ChatPanel({ filename, onReset }) {
  const [messages, setMessages] = useState([])
  const [threadId, setThreadId] = useState(null)
  const [stage, setStage] = useState(null)
  const [status, setStatus] = useState('idle') // idle | loading | interrupted | completed | error
  const [error, setError] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, status])

  async function handleSend(value) {
    setStatus('loading')
    setError('')
    setMessages((prev) => [...prev, { role: 'user', text: value }])

    try {
      const res = threadId
        ? await resumeChat(threadId, value)
        : await askQuestion(value, threadId)

      setThreadId(res.thread_id)

      const newMessages = []
      if (res.answer) newMessages.push({ role: 'assistant', text: res.answer })
      if (res.status === 'interrupted' && res.msg) {
        newMessages.push({ role: 'assistant', text: res.msg })
      }
      setMessages((prev) => [...prev, ...newMessages])
      setStage(res.status === 'interrupted' ? res.stage : null)
      setStatus(res.status)
    } catch (e) {
      setStatus('error')
      setError(e.message)
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-panel__header">
        <span className="chat-panel__filename">{filename}</span>
        <button className="chat-panel__reset" onClick={onReset}>
          새 문서로 시작하기
        </button>
      </div>

      <div className="chat-panel__history">
        {messages.map((m, i) => (
          <ChatMessage key={i} role={m.role} text={m.text} />
        ))}
        {status === 'loading' && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {status === 'error' && <p className="error-text">{error}</p>}

      {status === 'completed' ? (
        <div className="chat-panel__ended">
          <p>학습이 종료되었습니다.</p>
        </div>
      ) : (
        <StageInput stage={stage} onSubmit={handleSend} disabled={status === 'loading'} />
      )}
    </div>
  )
}
