import streamlit as st
import random

st.set_page_config(page_title="Slang & Meme Translator — Home", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero {
  background: linear-gradient(135deg, #F8FAFC 0%, #EEF2F7 100%);
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  padding: 48px 40px;
  box-shadow: 0 16px 40px rgba(17, 24, 39, 0.10);
  position: relative;
  overflow: hidden;
}
.hero::after {
  content: "";
  position: absolute;
  left: -120px; bottom: -140px; width: 380px; height: 380px;
  background: radial-gradient(closest-side, rgba(79,70,229,0.18), rgba(16,185,129,0.12));
  filter: blur(42px);
  border-radius: 50%;
  animation: float 10s ease-in-out infinite;
}
.hero-grid { display:flex; align-items:flex-start; gap:24px; }
.hero h1 {
  margin: 0;
  color: #111827;
  font-size: 2.6rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}
.grad { background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero p {
  margin: 10px 0 20px;
  color: #475569;
  font-size: 1.05rem;
  font-weight: 500;
}
.cta-row { display: flex; gap: 12px; align-items: center; }
.cta-primary {
  display: inline-flex; align-items:center; justify-content:center;
  padding: 14px 18px; border-radius: 12px; color: #fff; text-decoration: none;
  background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%);
  box-shadow: 0 10px 22px rgba(79, 70, 229, 0.35);
  font-weight: 800;
}
.cta-primary:hover { transform: translateY(-1px); box-shadow: 0 16px 28px rgba(79,70,229,0.45); }
.cta-secondary {
  display: inline-flex; align-items:center; justify-content:center;
  padding: 14px 18px; border-radius: 12px; color: #334155; text-decoration: none;
  background: #fff; border: 1px solid #e5e7eb;
  box-shadow: 0 8px 18px rgba(17,24,39,0.06);
  font-weight: 700;
}
.cta-secondary:hover { border-color: #818CF8; box-shadow: 0 10px 22px rgba(17,24,39,0.08); transform: translateY(-1px); }
.blob {
  position: absolute; right: -100px; top: -120px; width: 360px; height: 360px;
  background: radial-gradient(closest-side, rgba(99,102,241,0.18), rgba(16,185,129,0.12));
  filter: blur(40px);
  border-radius: 50%;
  animation: float 8s ease-in-out infinite;
}
@keyframes float { 0% { transform: translateY(0px) } 50% { transform: translateY(20px) } 100% { transform: translateY(0px) } }

.glass-chat {
  flex: 1;
  background: rgba(255,255,255,0.45);
  border: 1px solid rgba(255,255,255,0.6);
  border-radius: 20px;
  backdrop-filter: blur(12px);
  box-shadow: 0 18px 42px rgba(17,24,39,0.14);
  padding: 18px;
}
.glass-chat .row { display:flex; align-items:center; gap:12px; }
.bubble-glass {
  flex:1;
  background: linear-gradient(180deg, rgba(255,255,255,0.7), rgba(238,242,247,0.7));
  border: 1px solid rgba(229,231,235,0.9);
  border-radius: 14px;
  padding: 12px;
  color:#1f2937; font-weight:700; box-shadow: 0 8px 20px rgba(17,24,39,0.10);
}
.arrow {
  width: 40px; height: 40px; display:flex; align-items:center; justify-content:center;
  background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%); color:#fff; border-radius: 12px; box-shadow: 0 10px 22px rgba(79,70,229,0.35);
}
.bubble-sub { color:#64748b; font-weight:600; margin-top:4px; }
.emoji-glow { text-shadow: 0 0 8px rgba(99,102,241,0.45); }

.cards { margin-top: 26px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.card {
  background: #fff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 18px;
  box-shadow: 0 10px 24px rgba(17,24,39,0.08);
}
.card:hover { transform: translateY(-3px); box-shadow: 0 14px 32px rgba(17,24,39,0.12); transition: all 220ms ease; }
.card h3 { margin: 6px 0 6px; color: #111827; font-size: 1.05rem; font-weight: 800; }
.card p { margin: 0; color: #475569; font-size: 0.95rem; }
.chip { display:inline-flex; align-items:center; gap:8px; background:#EEF2F7; color:#334155; padding:8px 12px; border-radius:12px; font-weight:700; }
.trust { display:flex; gap:10px; margin-top: 12px; }
.trust .pill { background:#EEF2FF; color:#4338CA; border-color:#A5B4FC; }

.preview {
  margin-top: 18px; display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 16px;
}
.bubble {
  background: #fff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 14px;
  box-shadow: 0 10px 24px rgba(17,24,39,0.08);
}
.bubble:hover { transform: translateY(-2px); box-shadow: 0 14px 32px rgba(17,24,39,0.12); transition: all 200ms ease; }
.bubble h4 { margin: 0 0 8px; color:#111827; font-weight:800; }
.bubble .text { color:#1f2937; font-weight:700; }
.bubble .sub { color:#64748b; font-weight:600; }

.demo {
  margin-top: 28px; background:#fff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 18px;
  box-shadow: 0 10px 24px rgba(17,24,39,0.08);
}
.demo { animation: fadeUp 600ms ease-out both; }
.demo h3 { margin:0 0 8px; color:#111827; font-weight:800; }
.split { display:flex; gap:12px; }
.split .left { flex:1; }
.split .right { width: 36%; }
.pill {
  display:inline-flex; padding:6px 10px; border-radius:999px; background:#ECFDF5; color:#065F46; font-weight:700; border:1px solid #10B981;
}
.fadeUp { animation: fadeUp 640ms ease-out both; }
@keyframes fadeUp { 0% { opacity: 0; transform: translateY(12px);} 100% { opacity: 1; transform: translateY(0);} }
</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <section class="hero">
      <div class="blob"></div>
      <div class="hero-grid">
        <div style="flex:1.1;">
          <div class="chip">✨ Slang & Meme Translator</div>
          <h1 class="fadeUp">Understand internet slang, memes, and <span class="grad">Gen‑Z language</span> <span class="grad">instantly</span> using AI.</h1>
          <p>Translate casual posts, comments, and Hinglish code‑mix into clear, professional English — and back again.</p>
          <div class="cta-row">
            <a href="../" class="cta-primary">⚡ Try the Translator</a>
            <a href="https://github.com/neeraj214/cross-language-meme-slang-translator" target="_blank" class="cta-secondary">View on GitHub</a>
            <a href="#features" onclick="document.getElementById('features').scrollIntoView({behavior:'smooth'}); return false;" class="cta-secondary">Learn more</a>
          </div>
          <div class="trust">
            <div class="pill">Built on T5</div>
            <div class="pill">Hinglish support</div>
            <div class="pill">BLEU‑validated</div>
          </div>
        </div>
        <div class="glass-chat">
          <div class="row">
            <div class="bubble-glass">
              <div><span class="emoji-glow">💬</span> “that’s no cap, fr fr”</div>
              <div class="sub bubble-sub">before</div>
            </div>
            <div class="arrow">➜</div>
            <div class="bubble-glass">
              <div>“that is the truth, i am being serious.”</div>
              <div class="sub bubble-sub">after</div>
            </div>
          </div>
        </div>
      </div>
    </section>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div id="features" class="cards fadeUp" style="grid-template-columns: 1.3fr 1fr 1fr;">
      <div class="card">
        <div style="font-size:1.3rem; text-shadow: 0 0 8px rgba(99,102,241,0.45);">🕵️‍♂️</div>
        <h3>Slang Detection</h3>
        <p>Identifies emoji, abbreviations, and informal phrases for accurate meaning.</p>
      </div>
      <div class="card">
        <div style="font-size:1.3rem; text-shadow: 0 0 8px rgba(99,102,241,0.45);">🧠</div>
        <h3>Meme Context</h3>
        <p>Understands meme tone and intent to preserve humor and nuance.</p>
      </div>
      <div class="card">
        <div style="font-size:1.3rem; text-shadow: 0 0 8px rgba(99,102,241,0.45);">🌐</div>
        <h3>Multi‑Language</h3>
        <p>Handles English and Hinglish code‑mix for seamless translation.</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

examples = [
    ("bro’s cooked 💀", "he messed up badly."),
    ("that fit is fire 🔥", "the outfit looks amazing."),
    ("yaar mood off ho gaya 😒", "i’m not in a good mood."),
    ("ain’t no way 😭", "i can’t believe this."),
    ("Bro this meme is fire 💀", "This meme is extremely funny or impressive."),
]
ex_src, ex_tgt = random.choice(examples)

st.markdown(
    f"""
    <div class="preview">
      <div class="bubble">
        <h4>Slang</h4>
        <div class="text">{ex_src}</div>
        <div class="sub">sample input</div>
      </div>
      <div class="bubble">
        <h4>Meaning</h4>
        <div class="text">{ex_tgt}</div>
        <div class="sub">interpreted output</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="demo">
      <h3>Live Demo Preview</h3>
      <div class="split">
        <div class="left">
    """,
    unsafe_allow_html=True
)

user_text = st.text_input("Type some slang here…", value="That's no cap, fr fr", placeholder="e.g., That's no cap, fr fr")
go = st.button("Preview Translation", type="primary")

mapping = {
    "bro’s cooked": "he messed up badly.",
    "fit is fire": "the outfit looks amazing.",
    "mood off": "i’m not in a good mood.",
    "ain’t no way": "i can’t believe this.",
    "op": "overpowered or awesome.",
    "meme is fire": "this meme is extremely funny or impressive.",
    "no cap": "that is the truth.",
    "fr fr": "i am being serious.",
}

result = ""
if go:
    text = (user_text or "").lower()
    for k, v in mapping.items():
        if k in text:
            result = v
            break
    if not result and text.strip():
        result = "interpreted meaning not found — try the full translator."
    if not text.strip():
        result = "enter text to preview."

col_l, col_r = st.columns([1, 1])
with col_r:
    st.markdown("<div class='pill'>Preview</div>", unsafe_allow_html=True)
    st.write(result if result else "—")

st.markdown(
    """
        </div>
        <div class="right">
          <div class="bubble">
            <h4>Tip</h4>
            <div class="text">Use “Try the Translator” to run the real model.</div>
            <div class="sub">full bidirectional translation</div>
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)
