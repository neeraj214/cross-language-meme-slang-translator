import { useState } from 'react'
import ExampleChip from './ExampleChip'

type Direction = 'forward' | 'reverse'
type Props = {
  onTranslate?: (text: string, dir: Direction) => void
}

const examples = [
  "that's no cap, fr fr",
  "that fit is fire 🔥",
  "bro’s cooked 💀",
  "yaar mood off ho gaya 😒",
]

export default function TranslatorInput({ onTranslate }: Props) {
  const [text, setText] = useState('')
  const [dir, setDir] = useState<Direction>('forward')
  const [loading, setLoading] = useState(false)
  const disabled = text.trim().length === 0

  const run = () => {
    if (disabled || loading) return
    setLoading(true)
    onTranslate?.(text, dir)
    setTimeout(() => setLoading(false), 800)
  }

  return (
    <div className="rounded-xl border bg-card p-5 shadow-md">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold text-text/70">Type slang or Hinglish</div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setDir('forward')}
            className={`rounded-xl px-3 py-1.5 text-sm font-bold transition border ${dir === 'forward' ? 'bg-primary text-white border-primary' : 'bg-bg text-text hover:bg-card hover:shadow-md'}`}
          >
            Slang → English
          </button>
          <button
            type="button"
            onClick={() => setDir('reverse')}
            className={`rounded-xl px-3 py-1.5 text-sm font-bold transition border ${dir === 'reverse' ? 'bg-primary text-white border-primary' : 'bg-bg text-text hover:bg-card hover:shadow-md'}`}
          >
            English → Slang
          </button>
        </div>
      </div>

      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type some slang here…"
        className="mt-3 w-full rounded-xl border px-4 py-3 text-base shadow-inner focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
      />
      <div className="mt-1 text-xs text-text/60">Examples: “no cap” → truth, “fit is fire” → great outfit</div>

      <div className="mt-3 flex flex-wrap gap-2">
        {examples.map((e) => (
          <ExampleChip key={e} label={e} onClick={(label) => setText(label)} />
        ))}
      </div>

      <button
        type="button"
        disabled={disabled || loading}
        onClick={run}
        className={`mt-4 w-full rounded-xl px-4 py-3 text-base font-extrabold transition shadow-md focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${disabled || loading ? 'bg-primary/50 text-white cursor-not-allowed' : 'btn-cta bg-gradient-to-r from-[var(--primary)] to-[var(--secondary)] text-white hover:shadow-lg'}`}
      >
        {loading ? 'Translating…' : 'Try Translation'}
      </button>
    </div>
  )
}
