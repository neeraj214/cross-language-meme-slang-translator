import { useMemo } from 'react'

type Props = {
  input: string
  direction: 'forward' | 'reverse'
}

const dict: Record<string, string> = {
  'no cap': 'that is the truth',
  'fr fr': 'i am being serious',
  'fit is fire': 'the outfit looks amazing',
  'bro’s cooked': 'he messed up badly',
  'mood off': 'i am not in a good mood',
}

export default function DemoShowcase({ input, direction }: Props) {
  const output = useMemo(() => {
    const t = input.toLowerCase()
    const found = Object.keys(dict).find((k) => t.includes(k))
    if (!found) return 'interpreted meaning not found'
    return dict[found]
  }, [input])

  return (
    <div id="demo" className="rounded-xl border bg-card p-5 shadow-md">
      <div className="text-lg font-extrabold">Live Demo</div>
      <div className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="rounded-xl border bg-bg p-4 shadow-inner">
          <div className="text-sm font-bold text-text/70">Before</div>
          <div className="mt-2 text-base font-extrabold">{input || '—'}</div>
        </div>
        <div className="rounded-xl border bg-bg p-4 shadow-inner">
          <div className="text-sm font-bold text-text/70">After</div>
          <div className="mt-2 text-base font-extrabold">{direction === 'forward' ? output : 'slang style sample'}</div>
        </div>
      </div>
    </div>
  )
}
