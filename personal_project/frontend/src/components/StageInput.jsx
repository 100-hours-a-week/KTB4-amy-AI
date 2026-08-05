import { useState } from 'react'
import { STAGE_PLACEHOLDERS, YN_STAGES } from '../stages'

export default function StageInput({ stage, onSubmit, disabled }) {
  const [text, setText] = useState('')
  const isYN = YN_STAGES.has(stage)

  function submit(value) {
    const v = (value ?? text).trim()
    if (!v) return
    onSubmit(v)
    setText('')
  }

  const placeholder = stage
    ? STAGE_PLACEHOLDERS[stage]
    : '어떤 내용을 배우고 싶으신가요? (예: 1장부터 설명해줘)'

  return (
    <div className="stage-input">
      <form
        className="stage-input__row"
        onSubmit={(e) => {
          e.preventDefault()
          submit()
        }}
      >
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
        />
        <button type="submit" disabled={disabled}>
          전송
        </button>
      </form>
    </div>
  )
}
