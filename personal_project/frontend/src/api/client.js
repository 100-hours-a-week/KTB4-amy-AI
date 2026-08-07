const API_BASE = ''

let apiKey = null

export function setApiKey(key) {
  apiKey = key
}

function authHeaders(extra = {}) {
  return apiKey ? { ...extra, 'X-API-Key': apiKey } : extra
}

async function parseOrThrow(res) {
  if (!res.ok) {
    throw new Error(`요청 실패 (${res.status})`)
  }
  return res.json()
}

export async function verifyApiKey(key) {
  const res = await fetch(`${API_BASE}/api/verify`, {
    headers: { 'X-API-Key': key },
  })
  return res.ok
}

export async function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API_BASE}/api/upload`, {
    method: 'POST',
    headers: authHeaders(),
    body: formData,
  })
  return parseOrThrow(res)
}

export async function askQuestion(question, threadId) {
  const res = await fetch(`${API_BASE}/api/ask`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ question, thread_id: threadId ?? null }),
  })
  return parseOrThrow(res)
}

export async function resumeChat(threadId, reply) {
  const res = await fetch(`${API_BASE}/api/resume`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ thread_id: threadId, reply }),
  })
  return parseOrThrow(res)
}
