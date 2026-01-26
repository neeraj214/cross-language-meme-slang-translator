import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './pages/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: 'var(--primary)',
        secondary: 'var(--secondary)',
        accent: 'var(--accent)',
        bg: 'var(--background)',
        text: 'var(--text)',
        card: 'var(--card-bg)',
      },
      boxShadow: {
        mdx: '0 6px 18px rgba(10,36,99,0.12)',
        lgx: '0 12px 28px rgba(10,36,99,0.18)',
      },
    },
  },
  plugins: [],
}

export default config
