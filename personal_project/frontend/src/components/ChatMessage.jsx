import ReactMarkdown from 'react-markdown'

// CommonMark only closes a **bold** span at a delimiter that's "right-flanking". A closing `**`
// preceded by punctuation (e.g. a closing quote) and immediately followed by a non-space
// character (e.g. a Korean particle with no space) fails that check, so the whole span renders
// as literal asterisks instead of bold. Inserting a NBSP after the closing `**` in that specific
// case fixes the flanking rule without touching spans that already render correctly, and code
// spans/fences are skipped so example code isn't altered.
function fixBoldFlanking(text) {
  const boldFix = (segment) =>
    segment.replace(/\*\*([^*\n]+?)\*\*(?=[^\s*\p{P}])/gu, (match, inner) =>
      /\p{P}$/u.test(inner) ? `**${inner}** ` : match
    )

  return text
    .split(/(```[\s\S]*?```|`[^`\n]*`)/)
    .map((part, i) => (i % 2 === 0 ? boldFix(part) : part))
    .join('')
}

export default function ChatMessage({ role, text }) {
  return (
    <div className={`chat-message chat-message--${role}`}>
      <div className="chat-message__bubble">
        <div className="chat-message__markdown">
          <ReactMarkdown>{fixBoldFlanking(text)}</ReactMarkdown>
        </div>
      </div>
    </div>
  )
}
