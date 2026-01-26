import Link from 'next/link'

export default function Header() {
  return (
    <header className="w-full bg-bg">
      <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-white shadow-md">AI</span>
          <span className="text-xl font-extrabold">Slang & Meme Translator</span>
        </Link>
        <nav className="flex items-center gap-4">
          <Link href="/" className="rounded-xl px-3 py-2 text-sm font-semibold hover:bg-card hover:shadow-md transition">Home</Link>
          <Link href="/#demo" className="rounded-xl px-3 py-2 text-sm font-semibold hover:bg-card hover:shadow-md transition">Try Demo</Link>
          <a href="https://github.com/neeraj214/cross-language-meme-slang-translator" target="_blank" className="rounded-xl px-3 py-2 text-sm font-semibold border border-primary text-primary hover:bg-primary hover:text-white transition">GitHub</a>
        </nav>
      </div>
    </header>
  )
}
