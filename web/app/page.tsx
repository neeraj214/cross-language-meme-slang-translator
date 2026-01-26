'use client'

import { useState } from 'react'
import Header from '@/components/Header'
import TranslatorInput from '@/components/TranslatorInput'
import FeatureCard from '@/components/FeatureCard'
import DemoShowcase from '@/components/DemoShowcase'
import TrustBadge from '@/components/TrustBadge'

export default function Page() {
  const [input, setInput] = useState('')
  const [dir, setDir] = useState<'forward' | 'reverse'>('forward')

  const onTranslate = (text: string, d: 'forward' | 'reverse') => {
    setInput(text)
    setDir(d)
  }

  return (
    <main className="min-h-screen bg-bg">
      <Header />
      <section className="mx-auto max-w-7xl px-6 pt-10">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="rounded-xl border bg-card p-8 shadow-lg">
            <div className="text-4xl font-extrabold leading-tight">
              Understand internet slang, memes, and
              <span className="bg-gradient-to-r from-[var(--primary)] to-[var(--secondary)] bg-clip-text text-transparent"> Gen‑Z language </span>
              instantly using AI
            </div>
            <div className="mt-3 text-base text-text/80">Translate casual posts, comments, and Hinglish code‑mix into clear, professional English — and back again.</div>
            <div className="mt-4 flex items-center gap-2">
              <TrustBadge label="BLEU‑validated" variant="primary" />
              <TrustBadge label="Built on T5" variant="secondary" />
              <TrustBadge label="GitHub Stars" variant="accent" />
            </div>
            <div className="mt-6">
              <TranslatorInput onTranslate={onTranslate} />
            </div>
          </div>
          <div className="rounded-xl border bg-card p-6 shadow-lg">
            <div className="flex items-center justify-between">
              <div className="text-lg font-extrabold">Translation Preview</div>
              <div className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-r from-[var(--primary)] to-[var(--secondary)] text-white shadow-md">AI</div>
            </div>
            <div className="mt-4 rounded-xl border bg-white/60 backdrop-blur-md p-4 shadow-md">
              <div className="grid grid-cols-[1fr_60px_1fr] items-center gap-3">
                <div className="rounded-xl border bg-bg p-3 shadow-inner">
                  <div className="text-sm font-bold text-text/70">Before</div>
                  <div className="mt-2 font-extrabold">{input || "that's no cap, fr fr"}</div>
                </div>
                <div className="flex items-center justify-center rounded-xl bg-gradient-to-r from-[var(--primary)] to-[var(--secondary)] text-white shadow-md">→</div>
                <div className="rounded-xl border bg-bg p-3 shadow-inner">
                  <div className="text-sm font-bold text-text/70">After</div>
                  <div className="mt-2 font-extrabold">{dir === 'forward' ? 'that is the truth, i am being serious' : 'slang style sample'}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <section className="mt-10 grid grid-cols-1 gap-4 md:grid-cols-3">
          <FeatureCard icon={<span>🕵️‍♂️</span>} title="Slang Detection" description="Emoji, abbreviations, and informal phrases recognized." className="md:col-span-2" />
          <FeatureCard icon={<span>🧠</span>} title="Meme Context" description="Preserves tone and humor with context awareness." />
          <FeatureCard icon={<span>🌐</span>} title="Multi‑Language" description="Handles English and Hinglish code‑mix seamlessly." />
        </section>

        <section className="mt-10">
          <DemoShowcase input={input} direction={dir} />
        </section>
      </section>

      <footer className="mt-12 border-t bg-card">
        <div className="mx-auto max-w-7xl px-6 py-6 flex flex-wrap items-center justify-between gap-3">
          <a href="https://github.com/neeraj214/cross-language-meme-slang-translator" className="rounded-xl px-3 py-2 text-sm font-semibold border border-primary text-primary hover:bg-primary hover:text-white transition">GitHub</a>
          <div className="text-sm text-text/70">BLEU Badge • T3 Stack • Tailwind</div>
        </div>
      </footer>
    </main>
  )
}
