export default function TypingIndicator() {
  return (
    <div className="chat-message chat-message--assistant">
      <div className="chat-message__bubble chat-message__bubble--typing">
        <span className="typing-dot" />
        <span className="typing-dot" />
        <span className="typing-dot" />
      </div>
    </div>
  )
}
