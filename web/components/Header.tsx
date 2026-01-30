import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function Header() {
  const pathname = usePathname()
  const isActive = (href: string) => pathname === href
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-card/80 backdrop-blur">
      <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-white shadow-md">AI</span>
          <span className="text-xl font-extrabold">Slang & Meme Translator</span>
        </Link>
        <nav className="flex items-center gap-2">
          <Link
            href="/"
            className={`rounded-xl px-3 py-2 text-sm font-semibold transition ${isActive('/') ? 'bg-primary text-white' : 'hover:bg-card hover:shadow-md'}`}
          >
            Home
          </Link>
          <Link
            href="/translator"
            className={`rounded-xl px-3 py-2 text-sm font-semibold transition ${isActive('/translator') ? 'bg-secondary text-white' : 'hover:bg-card hover:shadow-md'}`}
          >
            Translator
          </Link>
          <Link
            href="/about"
            className={`rounded-xl px-3 py-2 text-sm font-semibold transition ${isActive('/about') ? 'bg-accent text-white' : 'hover:bg-card hover:shadow-md'}`}
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
        </nav>
      </div>
    </header>
  )
}
