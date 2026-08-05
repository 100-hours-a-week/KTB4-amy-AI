import { useState } from 'react'
import UploadPanel from './UploadPanel'
import ChatPanel from './ChatPanel'

export default function NotebookWorkspace() {
  const [phase, setPhase] = useState('upload') // 'upload' | 'chat'
  const [filename, setFilename] = useState('')
  const [chatKey, setChatKey] = useState(0)

  function handleUploaded(name) {
    setFilename(name)
    setPhase('chat')
  }

  function handleReset() {
    setPhase('upload')
    setFilename('')
    setChatKey((k) => k + 1)
  }

  return (
    <div className="notebook-workspace">
      {phase === 'upload' ? (
        <UploadPanel onUploaded={handleUploaded} />
      ) : (
        <ChatPanel key={chatKey} filename={filename} onReset={handleReset} />
      )}
    </div>
  )
}
