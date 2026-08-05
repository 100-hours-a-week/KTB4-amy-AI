import { useState } from 'react'
import { uploadFile } from '../api/client'

export default function UploadPanel({ onUploaded }) {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState('')

  async function handleUpload() {
    if (!file) return
    setStatus('uploading')
    setError('')
    try {
      const res = await uploadFile(file)
      onUploaded(res.filename ?? file.name)
    } catch (e) {
      setStatus('error')
      setError(e.message)
    }
  }

  return (
    <div className="upload-panel">
      <h2>학습 자료 업로드</h2>
      <p>PDF 파일을 업로드하면 문서 기반 학습을 시작할 수 있어요.</p>
      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        disabled={status === 'uploading'}
      />
      {file && <p className="upload-panel__selected">선택된 파일: {file.name}</p>}
      <button onClick={handleUpload} disabled={!file || status === 'uploading'}>
        업로드
      </button>
      {status === 'uploading' && (
        <div className="upload-panel__loading">
          <span className="typing-dot" />
          <span className="typing-dot" />
          <span className="typing-dot" />
          <span>문서를 분석하는 중입니다...</span>
        </div>
      )}
      {status === 'error' && <p className="error-text">{error}</p>}
    </div>
  )
}
