'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useEffect, useState } from 'react'

export default function Header() {
  const pathname = usePathname()
  const [theme, setTheme] = useState<'dark' | 'light'>('dark')
  useEffect(() => {
    const saved = localStorage.getItem('theme') as 'dark' | 'light' | null
    if (saved) setTheme(saved)
  }, [])
  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.body.classList.toggle('light', theme === 'light')
      localStorage.setItem('theme', theme)
    }
  }, [theme])
  const isActive = (href: string) => pathname === href
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-card/80 backdrop-blur">
      <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 nav-link">
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-white shadow-md">AI</span>
          <span className="text-xl font-extrabold">Slang & Meme Translator</span>
        </Link>
        <nav className="flex items-center gap-2">
          <Link
            href="/"
            className={`nav-link rounded-xl px-3 py-2 text-sm font-semibold transition ${isActive('/') ? 'bg-primary text-white' : 'hover:bg-card hover:shadow-md'}`}
          >
            Home
          </Link>
          <Link
            href="/translator"
            className={`nav-link rounded-xl px-3 py-2 text-sm font-semibold transition ${isActive('/translator') ? 'bg-secondary text-white' : 'hover:bg-card hover:shadow-md'}`}
          >
            Translator
          </Link>
          <Link
            href="/about"
            className={`nav-link rounded-xl px-3 py-2 text-sm font-semibold transition ${isActive('/about') ? 'bg-accent text-white' : 'hover:bg-card hover:shadow-md'}`}
          >
            About
          </Link>
          <a
            href="https://github.com/neeraj214/cross-language-meme-slang-translator"
            target="_blank"
            className="rounded-xl px-3 py-2 text-sm font-semibold border border-primary text-primary hover:bg-primary hover:text-white transition"
          >
            GitHub
          </a>
          <button
            type="button"
            onClick={() => setTheme(t => (t === 'dark' ? 'light' : 'dark'))}
            className="ml-2 rounded-xl px-3 py-2 text-sm font-semibold border border-primary text-primary hover:bg-primary hover:text-white transition"
          >
            {theme === 'dark' ? 'Light' : 'Dark'}
          </button>
        </nav>
      </div>
    </header>
  )
}
