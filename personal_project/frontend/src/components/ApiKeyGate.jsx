import { useState } from 'react'
import { setApiKey, verifyApiKey } from '../api/client'

export default function ApiKeyGate({ children }) {
  const [verified, setVerified] = useState(false)
  const [key, setKey] = useState('')
  const [status, setStatus] = useState('idle') // idle | verifying | error
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    if (!key.trim()) return
    setStatus('verifying')
    setError('')
    try {
      const ok = await verifyApiKey(key)
      if (ok) {
        setApiKey(key)
        setVerified(true)
      } else {
        setStatus('error')
        setError('비밀번호가 올바르지 않습니다')
      }
    } catch {
      setStatus('error')
      setError('비밀번호가 올바르지 않습니다')
    }
  }

  if (verified) return children

  return (
    <div className="api-key-gate">
      <form className="api-key-gate__form" onSubmit={handleSubmit}>
        <h2>비밀번호 입력</h2>
        <p>계속하려면 비밀번호를 입력하세요.</p>
        <input
          type="password"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          placeholder="비밀번호"
          disabled={status === 'verifying'}
          autoFocus
        />
        <button type="submit" disabled={status === 'verifying' || !key.trim()}>
          {status === 'verifying' ? '확인 중...' : '입장하기'}
        </button>
        {status === 'error' && <p className="error-text">{error}</p>}
      </form>
    </div>
  )
}
