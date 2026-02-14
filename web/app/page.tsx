'use client'

import TrustBadge from '@/components/TrustBadge'
import FeatureCard from '@/components/FeatureCard'
import HeroIllustration from '@/components/HeroIllustration'
import Testimonials from '@/components/Testimonials'
import { useEffect, useRef, useState } from 'react'

export default function Page() {
  const heroRef = useRef<HTMLDivElement | null>(null)
  const [mounted, setMounted] = useState(false)
  useEffect(() => {
    setMounted(true)
    const handleMouse = (e: MouseEvent) => {
      if (!heroRef.current) return
      const rect = heroRef.current.getBoundingClientRect()
      const x = (e.clientX - rect.left) / rect.width - 0.5
      const y = (e.clientY - rect.top) / rect.height - 0.5
      heroRef.current.style.transform = `perspective(900px) rotateX(${y * -2}deg) rotateY(${x * 2}deg)`
    }
    document.addEventListener('mousemove', handleMouse)
    return () => document.removeEventListener('mousemove', handleMouse)
  }, [])
  useEffect(() => {
    const items = Array.from(document.querySelectorAll('.reveal'))
    const io = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) entry.target.classList.add('show')
        })
      },
      { threshold: 0.15 }
    )
    items.forEach(el => io.observe(el))
    return () => io.disconnect()
  }, [])
  return (
    <main className="min-h-screen bg-bg page-enter">
      <section className="sticky top-0 z-40 border-b bg-card/80 backdrop-blur">
        <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-white shadow-md">AI</span>
            <span className="text-xl font-extrabold">Slang & Meme Translator</span>
          </div>
          <div className="flex items-center gap-2">
            <a href="/translator" className="rounded-xl bg-gradient-to-r from-[var(--primary)] to-[var(--secondary)] px-4 py-2 text-sm font-extrabold text-white shadow-md">Try the Translator</a>
            <a href="https://github.com/neeraj214/cross-language-meme-slang-translator" target="_blank" className="rounded-xl border border-primary px-4 py-2 text-sm font-semibold text-primary hover:bg-primary hover:text-white transition">GitHub</a>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 pt-14">
        <div ref={heroRef} className="relative overflow-hidden rounded-2xl border bg-card p-12 shadow-lg hero-gradient hero-xl animate-fade-up">
          <div className="aurora" />
          <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-2">
            <div>
              <div className="text-6xl md:text-7xl font-extrabold leading-tight">
                <span className="bg-gradient-to-r from-[var(--primary)] to-[var(--accent)] bg-clip-text text-transparent">Understand Internet Slang</span>, Memes & Gen‑Z Language Instantly
              </div>
              <div className="mt-3 text-base text-text/80">Translate slang, Hinglish, and casual internet language into clear English using AI.</div>
              <div className="mt-4 flex flex-wrap items-center gap-2">
                <TrustBadge label="BLEU‑validated" variant="primary" />
                <TrustBadge label="Built on T5" variant="secondary" />
                <TrustBadge label="GitHub Stars" variant="accent" />
              </div>
              <div className="mt-6 flex items-center gap-3">
                <a href="/translator" className="btn-cta rounded-xl bg-gradient-to-r from-[var(--primary)] to-[var(--accent)] px-5 py-3 text-sm font-extrabold text-white shadow-md transition hover:shadow-lg">Try It Now</a>
                <a href="#demo" className="btn-cta rounded-xl border border-primary px-5 py-3 text-sm font-extrabold text-primary transition hover:bg-primary hover:text-white">See Demo</a>
              </div>
            </div>
            <div className="relative">
              <div className="blob" />
              <div className="glass rounded-2xl border p-6 shadow-lg">
                <div className="flex items-center justify-between">
                  <div className="text-lg font-extrabold">Visual Preview</div>
                  <div className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-r from-[var(--primary)] to-[var(--secondary)] text-white shadow-md">AI</div>
                </div>
                <div className="mt-4 rounded-xl border bg-bg p-3 shadow-inner">
                  <HeroIllustration />
                </div>
              </div>
            </div>
          </div>
        </div>

        <section className="mt-10 grid grid-cols-1 gap-4 md:grid-cols-4 animate-stagger">
          <FeatureCard icon={<span>💬</span>} title="Slang → English" description="Clean, accurate meanings for modern slang." />
          <FeatureCard icon={<span>✨</span>} title="English → Slang" description="Generate casual, meme‑aware phrasing." />
          <FeatureCard icon={<span>🇮🇳</span>} title="Hinglish Support" description="Code‑mixed Hindi‑English understanding." />
          <FeatureCard icon={<span>🧠</span>} title="AI Context" description="Tone‑aware translation for intent." />
        </section>

        <section className="mt-12 grid grid-cols-1 gap-6 md:grid-cols-3">
          <div className="rounded-2xl border bg-card p-6 shadow-mdx reveal">
            <div className="text-lg font-extrabold">How It Works</div>
            <div className="mt-3 grid grid-cols-3 gap-3 text-sm text-text/80">
              <div className="glass rounded-xl p-4">
                <div className="text-primary font-bold">1</div>
                <div className="mt-2">Enter slang or Hinglish</div>
              </div>
              <div className="glass rounded-xl p-4">
                <div className="text-primary font-bold">2</div>
                <div className="mt-2">AI processes context</div>
              </div>
              <div className="glass rounded-xl p-4">
                <div className="text-primary font-bold">3</div>
                <div className="mt-2">Get clean translation</div>
              </div>
            </div>
          </div>
          <div className="rounded-2xl border bg-card p-6 shadow-mdx reveal">
            <div className="text-lg font-extrabold">Who Benefits</div>
            <div className="mt-3 grid grid-cols-2 gap-2 text-sm text-text/80">
              <div className="rounded-xl border bg-bg p-3 shadow-inner">Students</div>
              <div className="rounded-xl border bg-bg p-3 shadow-inner">Creators</div>
              <div className="rounded-xl border bg-bg p-3 shadow-inner">Professionals</div>
              <div className="rounded-xl border bg-bg p-3 shadow-inner">Social media users</div>
            </div>
          </div>
          <div className="rounded-2xl border bg-card p-6 shadow-mdx reveal">
            <div className="text-lg font-extrabold">Start Translating Smarter</div>
            <div className="mt-3 text-sm text-text/80">Try the focused Translator app with clean inputs, controls, and outputs.</div>
            <a href="/translator" className="mt-4 inline-flex rounded-xl bg-gradient-to-r from-[var(--primary)] to-[var(--secondary)] px-4 py-2 text-sm font-extrabold text-white shadow-md">Open Translator</a>
          </div>
        </section>

        <section id="demo" className="mt-12 rounded-2xl border bg-card p-8 shadow-mdx reveal">
          <div className="text-lg font-extrabold">Live Demo</div>
          <div className="mt-3 grid grid-cols-1 gap-4 md:grid-cols-2">
            <textarea className="rounded-xl border bg-bg p-4" placeholder="Type slang or Hinglish here..." rows={4} />
            <div className="rounded-xl border bg-bg p-4 shadow-inner">
              <HeroIllustration />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-3">
            <a href="/translator" className="btn-cta rounded-xl bg-gradient-to-r from-[var(--primary)] to-[var(--accent)] px-5 py-3 text-sm font-extrabold text-white shadow-md transition hover:shadow-lg">Open Full Translator</a>
            <a href="/" className="rounded-xl px-5 py-3 text-sm font-semibold text-text/80 hover:text-white transition">Learn more</a>
          </div>
        </section>
        <section className="mt-12 reveal">
          <Testimonials />
        </section>
        <section className="mt-12 rounded-2xl border bg-gradient-to-r from-[rgba(91,107,255,0.18)] to-[rgba(167,139,250,0.18)] p-8 shadow-mdx reveal">
          <div className="text-2xl font-extrabold">Ready to translate smarter?</div>
          <div className="mt-2 text-text/80">Open the app to see context-aware AI translations.</div>
          <div className="mt-4">
            <a href="/translator" className="btn-cta rounded-xl bg-gradient-to-r from-[var(--primary)] to-[var(--accent)] px-5 py-3 text-sm font-extrabold text-white shadow-md transition hover:shadow-lg">Open Translator</a>
          </div>
        </section>
      </section>

      <footer className="mt-12 border-t bg-card">
        <div className="mx-auto max-w-7xl px-6 py-6 flex flex-wrap items-center justify-between gap-3">
          <a href="https://github.com/neeraj214/cross-language-meme-slang-translator" className="rounded-xl px-3 py-2 text-sm font-semibold border border-primary text-primary hover:bg-primary hover:text-white transition">GitHub</a>
          <div className="text-sm text-text/70">Clean UI • Tailwind • Next.js</div>
        </div>
      </footer>
    </main>
  )
}
