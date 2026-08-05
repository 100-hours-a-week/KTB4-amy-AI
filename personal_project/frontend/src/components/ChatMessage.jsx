import ReactMarkdown from 'react-markdown'

export default function ChatMessage({ role, text }) {
  return (
    <div className={`chat-message chat-message--${role}`}>
      <div className="chat-message__bubble">
        <div className="chat-message__markdown">
          <ReactMarkdown>{text}</ReactMarkdown>
        </div>
      </div>
    </div>
  )
}
