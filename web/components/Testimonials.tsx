import { useEffect, useRef } from 'react'

export default function Testimonials() {
  const trackRef = useRef<HTMLDivElement | null>(null)
  useEffect(() => {
    const el = trackRef.current
    if (!el) return
    let start = performance.now()
    let raf = 0
    const loop = (t: number) => {
      const delta = (t - start) / 1000
      const x = (delta * 40) % 100
      el.style.transform = `translateX(-${x}%)`
      raf = requestAnimationFrame(loop)
    }
    raf = requestAnimationFrame(loop)
    return () => cancelAnimationFrame(raf)
  }, [])
  return (
    <div className="overflow-hidden rounded-2xl border bg-card shadow-mdx">
      <div className="px-6 py-4 text-lg font-extrabold">Loved by learners</div>
      <div className="relative h-40">
        <div ref={trackRef} className="absolute left-0 top-0 flex w-[200%] gap-4 px-6 py-2">
          <TestimonialCard name="Ananya" role="Student" text="Helps me decode slang fast for assignments." />
          <TestimonialCard name="Rohit" role="Creator" text="Great for caption ideas with the right tone." />
          <TestimonialCard name="Meera" role="Professional" text="Clarifies informal messages without losing intent." />
          <TestimonialCard name="Kabir" role="Social Media" text="Makes meme lingo understandable instantly." />
        </div>
      </div>
    </div>
  )
}

function TestimonialCard({ name, role, text }: { name: string; role: string; text: string }) {
  return (
    <div className="min-w-[320px] glass rounded-xl border p-4 shadow-mdx">
      <div className="text-sm text-text/80">{text}</div>
      <div className="mt-3 flex items-center gap-2">
        <div className="inline-flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-r from-[var(--primary)] to-[var(--accent)] text-white">★</div>
        <div className="text-sm font-semibold">{name}</div>
        <div className="text-xs text-text/60">{role}</div>
      </div>
    </div>
  )
}
