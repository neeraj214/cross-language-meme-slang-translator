'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import ExampleChip from '@/components/ExampleChip'
import DemoShowcase from '@/components/DemoShowcase'

export default function TranslatorPage() {
  const [text, setText] = useState('')
  const [direction, setDirection] = useState<'forward' | 'reverse'>('forward')
  const [style, setStyle] = useState<'Neutral' | 'Casual' | 'Meme-heavy'>('Neutral')
  const [tone, setTone] = useState<'Formal' | 'Informal' | 'Professional'>('Formal')
  const [output, setOutput] = useState('')
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const maxLen = 400
  useEffect(() => {
    if (!copied) return
    const t = setTimeout(() => setCopied(false), 1200)
    return () => clearTimeout(t)
  }, [copied])

  const runTranslate = async () => {
    if (!text.trim()) return
    setLoading(true)
    try {
      const res = await fetch('/api/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, direction }),
      })
      const data = await res.json()
      const out = typeof data?.output === 'string' ? data.output : ''
      setOutput(out)
    } catch {
      setOutput('translation failed')
    } finally {
      setLoading(false)
    }
  }

  const disabled = !text.trim() || loading

  return (
    <main className="min-h-screen bg-bg page-enter">
      <section className="sticky top-0 z-40 border-b bg-card/80 backdrop-blur">
        <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-white shadow-md">AI</span>
            <span className="text-xl font-extrabold">Translator</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-sm text-text/70">Slang ↔ English • Hinglish</div>
            <Link href="/" className="rounded-xl bg-gradient-to-r from-[var(--primary)] to-[var(--secondary)] px-4 py-2 text-sm font-extrabold text-white shadow-md">
              Home
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 pt-8 space-y-8">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 rounded-2xl border bg-card p-6 shadow-mdx animate-fade-up">
            <div className="flex items-center justify-between">
              <div className="text-lg font-extrabold">Input</div>
              <button
                type="button"
                onClick={() => setText('')}
                className="rounded-xl px-3 py-2 text-xs font-semibold border hover:bg-card transition"
              >
                Clear
              </button>
            </div>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Type slang, Hinglish, or casual internet language here…"
              maxLength={maxLen}
              className="mt-3 w-full h-48 rounded-xl border bg-bg p-4 text-base shadow-inner focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <div className="mt-2 flex items-center justify-between text-xs text-text/70">
              <div>Tip: Try idioms, memes, or Hinglish phrases</div>
              <div>{text.length}/{maxLen}</div>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {[
                "that's no cap, fr fr",
                "that fit is fire 🔥",
                "bro’s cooked 💀",
                "yaar mood off ho gaya 😒",
              ].map((e) => (
                <ExampleChip key={e} label={e} onClick={(label) => setText(label)} />
              ))}
            </div>
          </div>

          <div className="rounded-2xl border bg-card p-6 shadow-mdx animate-fade-up">
            <div className="text-lg font-extrabold">Controls</div>
            <div className="mt-3">
              <label className="text-sm font-semibold text-text/70">Direction</label>
              <div className="mt-2 grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => setDirection('forward')}
                  className={`rounded-xl px-3 py-2 text-sm font-bold border transition ${direction === 'forward' ? 'bg-primary text-white border-primary' : 'bg-bg text-text border-primary/40 hover:border-primary'}`}
                >
                  Slang → English
                </button>
                <button
                  type="button"
                  onClick={() => setDirection(direction === 'forward' ? 'reverse' : 'forward')}
                  className="rounded-xl px-3 py-2 text-sm font-bold border bg-bg text-text hover:bg-card transition"
                >
                  Swap
                </button>
                <button
                  type="button"
                  onClick={() => setDirection('reverse')}
                  className={`rounded-xl px-3 py-2 text-sm font-bold border transition ${direction === 'reverse' ? 'bg-secondary text-white border-secondary' : 'bg-bg text-text border-secondary/40 hover:border-secondary'}`}
                >
                  English → Slang
                </button>
              </div>
            </div>
            <div className="mt-4">
              <label className="text-sm font-semibold text-text/70">Style</label>
              <select
                value={style}
                onChange={(e) => setStyle(e.target.value as any)}
                className="mt-2 w-full rounded-xl border bg-bg p-2 text-sm focus:outline-none focus:ring-2 focus:ring-secondary"
              >
                <option>Neutral</option>
                <option>Casual</option>
                <option>Meme-heavy</option>
              </select>
            </div>
            <div className="mt-4">
              <label className="text-sm font-semibold text-text/70">Tone</label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value as any)}
                className="mt-2 w-full rounded-xl border bg-bg p-2 text-sm focus:outline-none focus:ring-2 focus:ring-secondary"
              >
                <option>Formal</option>
                <option>Informal</option>
                <option>Professional</option>
              </select>
            </div>
            <button
              type="button"
              disabled={disabled}
              onClick={runTranslate}
              className={`mt-6 w-full rounded-xl px-4 py-3 text-base font-extrabold transition shadow-md focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${disabled ? 'bg-primary/50 text-white cursor-not-allowed' : 'btn-cta bg-gradient-to-r from-[var(--primary)] to-[var(--secondary)] text-white'}`}
            >
              {loading ? 'Translating…' : 'Translate'}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 rounded-2xl border bg-card p-6 shadow-mdx animate-fade-up">
            <div className="flex items-center justify-between">
              <div className="text-lg font-extrabold">Output</div>
              {output && !loading ? (
                <div className="inline-flex items-center gap-2 rounded-xl border px-3 py-1 text-xs text-text/80">
                  <span className="inline-flex h-5 w-5 items-center justify-center rounded bg-primary text-white">✓</span>
                  Translated
                </div>
              ) : null}
            </div>
            <div className="mt-3 rounded-xl border bg-bg p-4 shadow-inner min-h-[160px]">
              {loading ? (
                <div className="animate-pulse space-y-2">
                  <div className="h-4 w-3/4 rounded bg-card" />
                  <div className="h-4 w-2/3 rounded bg-card" />
                  <div className="h-4 w-1/2 rounded bg-card" />
                </div>
              ) : (
                <div className="text-base font-extrabold">{output || '—'}</div>
              )}
            </div>
            <div className="mt-3 flex items-center gap-2">
              <button
                type="button"
                onClick={() => {
                  if (!output) return
                  navigator.clipboard.writeText(output)
                  setCopied(true)
                }}
                className={`rounded-xl border px-3 py-2 text-sm font-semibold transition ${output ? 'bg-bg hover:bg-card' : 'bg-bg/60 cursor-not-allowed'}`}
              >
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
          </div>

          <div className="rounded-2xl border bg-card p-6 shadow-mdx animate-fade-up">
            <div className="text-lg font-extrabold">Visual Preview</div>
            <div className="mt-3">
              <DemoShowcase input={text} direction={direction} />
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}
