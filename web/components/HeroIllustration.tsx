export default function HeroIllustration() {
  return (
    <svg
      className="w-full h-auto"
      viewBox="0 0 600 360"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="var(--primary)" />
          <stop offset="100%" stopColor="var(--secondary)" />
        </linearGradient>
      </defs>
      <rect x="0" y="0" width="600" height="360" rx="18" fill="#ffffff" />
      <g filter="url(#shadow)">
        <rect x="36" y="40" width="240" height="98" rx="16" fill="#F8F9FA" stroke="#e5e7eb" />
        <text x="52" y="72" fontSize="16" fontWeight="700" fill="#2D3436">“that’s no cap, fr fr”</text>
        <text x="52" y="98" fontSize="12" fill="#6b7280">before</text>
      </g>
      <g>
        <rect x="324" y="40" width="240" height="98" rx="16" fill="#F8F9FA" stroke="#e5e7eb" />
        <text x="340" y="72" fontSize="16" fontWeight="700" fill="#2D3436">“that is the truth”</text>
        <text x="340" y="98" fontSize="12" fill="#6b7280">after</text>
      </g>
      <circle cx="300" cy="88" r="22" fill="url(#g1)"></circle>
      <text x="292" y="94" fontSize="14" fontWeight="800" fill="#fff">→</text>

      <g>
        <rect x="36" y="180" width="170" height="90" rx="16" fill="#F8F9FA" stroke="#e5e7eb" />
        <text x="56" y="214" fontSize="14" fontWeight="700" fill="#2D3436">💬 Chat bubble</text>
      </g>
      <g>
        <rect x="226" y="180" width="170" height="90" rx="16" fill="#F8F9FA" stroke="#e5e7eb" />
        <text x="246" y="214" fontSize="14" fontWeight="700" fill="#2D3436">🧠 AI assist</text>
      </g>
      <g>
        <rect x="416" y="180" width="170" height="90" rx="16" fill="#F8F9FA" stroke="#e5e7eb" />
        <text x="436" y="214" fontSize="14" fontWeight="700" fill="#2D3436">✨ Transform</text>
      </g>

      <style>
        {`.pulse { animation: p 2.4s ease-in-out infinite } @keyframes p { 0%,100%{ opacity:.85 } 50%{ opacity:1 } }`}
      </style>
    </svg>
  )
}
