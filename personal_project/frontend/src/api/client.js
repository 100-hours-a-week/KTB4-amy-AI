const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function parseOrThrow(res) {
  if (!res.ok) {
    throw new Error(`요청 실패 (${res.status})`)
  }
  return res.json()
}

export async function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  })
  return parseOrThrow(res)
}

export async function askQuestion(question, threadId) {
  const res = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, thread_id: threadId ?? null }),
  })
  return parseOrThrow(res)
}

export async function resumeChat(threadId, reply) {
  const res = await fetch(`${API_BASE}/resume`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ thread_id: threadId, reply }),
  })
  return parseOrThrow(res)
}
