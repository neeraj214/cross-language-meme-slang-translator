import streamlit as st
import torch
from transformers import T5ForConditionalGeneration, T5TokenizerFast
import os
import csv
import json
import glob
import random

# Set page configuration
st.set_page_config(
    page_title="Slang/Meme Translator",
    page_icon="🔁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Web-App Look
def local_css():
    st.markdown("""
        <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Main Container Styling */
        .reportview-container { background: #F7F9FC; }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #f0f0f0;
        }

        /* Card Styling for Metrics */
        div[data-testid="metric-container"] {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: all 0.3s ease;
        }
        div[data-testid="metric-container"]:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            transform: translateY(-2px);
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.9rem;
            color: #666;
            font-weight: 600;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.8rem;
            color: #10B981;
            font-weight: 800;
        }

        /* Button Styling */
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            height: 3.6em;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.2s ease-in-out;
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Primary Button (Translate) */
        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%);
            color: white;
        }
        .stButton>button[kind="primary"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35);
        }
        .cta-disabled .stButton>button {
            opacity: 0.55;
            cursor: not-allowed;
            box-shadow: none;
        }

        /* Secondary Button (Example) */
        .stButton>button[kind="secondary"] {
            background-color: #f8f9fa;
            color: #333;
            border: 1px solid #e0e0e0;
        }
        .stButton>button[kind="secondary"]:hover {
            background-color: #f1f3f5;
            border-color: #ced4da;
            color: #000;
        }

        /* Text Area Styling */
        .stTextArea textarea {
            font-size: 16px !important;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            padding: 15px;
            background-color: #ffffff;
            transition: border-color 0.2s;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.01);
        }
        .stTextArea textarea:focus {
            border-color: #4F46E5;
            box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
        }
        .stTextArea textarea::placeholder {
            color: #9CA3AF;
        }

        /* Headers */
        h1 {
            color: #1a1a1a;
            font-weight: 800;
            letter-spacing: -0.5px;
        }
        h2, h3 {
            color: #333;
            font-weight: 700;
        }

        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px;
            color: #666;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            color: #4F46E5;
            border-bottom-color: #4F46E5;
        }

        /* Custom Alert/Info Boxes */
        .stAlert {
            border-radius: 8px;
            border: none;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
        
        /* Skeleton Loader */
        .skeleton {
            height: 220px;
            border-radius: 12px;
            background: linear-gradient(90deg, #f2f4f7 25%, #eaeef3 37%, #f2f4f7 63%);
            background-size: 400% 100%;
            animation: shimmer 1.4s ease-in-out infinite;
            border: 1px solid #e5e7eb;
        }
        @keyframes shimmer {
          0% { background-position: 100% 0; }
          100% { background-position: -100% 0; }
        }
        
        </style>
    """, unsafe_allow_html=True)

local_css()

# --- Configuration & Constants ---
FORWARD_MODEL_PATH = os.environ.get("FORWARD_MODEL", "outputs/checkpoints/t5-small-forward-ep5-lr3e4-64")
REVERSE_MODEL_PATH = os.environ.get("REVERSE_MODEL", "outputs/checkpoints/t5-small-reverse-ep5-lr3e4-64")
HINGLISH_FORWARD_MODEL_PATH = os.environ.get("HINGLISH_FORWARD_MODEL", "outputs/checkpoints/t5-small-hinglish-forward-ep10-lr0.0002-64")
HINGLISH_REVERSE_MODEL_PATH = os.environ.get("HINGLISH_REVERSE_MODEL", "outputs/checkpoints/t5-small-hinglish-reverse-ep10-lr0.0002-64")
FORWARD_MODEL_ID = os.environ.get("FORWARD_MODEL_ID", None)
REVERSE_MODEL_ID = os.environ.get("REVERSE_MODEL_ID", None)
HINGLISH_FORWARD_MODEL_ID = os.environ.get("HINGLISH_FORWARD_MODEL_ID", None)
HINGLISH_REVERSE_MODEL_ID = os.environ.get("HINGLISH_REVERSE_MODEL_ID", None)
HF_TOKEN = os.environ.get("HF_TOKEN", None)
try:
    if not HF_TOKEN:
        HF_TOKEN = st.secrets.get("HF_TOKEN", None)
except Exception:
    HF_TOKEN = HF_TOKEN
FALLBACK_MODEL = os.environ.get("FALLBACK_MODEL", "t5-small")
MAX_SOURCE_LEN = 128
MAX_TARGET_LEN = 64
APPLY_TASK_PREFIX = False 

# --- Helper Functions ---
def build_prefix(language: str, direction: str, style: str) -> str:
    style_tag = f" style: {style.lower()}" if style and style.lower() != "neutral" else ""
    if language == "Hinglish":
        if direction == "forward":
            return f"translate hinglish slang to english:{style_tag}".strip()
        else:
            return f"translate english to hinglish slang:{style_tag}".strip()
    else:
        if direction == "forward":
            return f"translate english slang to english:{style_tag}".strip()
        else:
            return f"translate english to slang:{style_tag}".strip()

def load_metrics():
    metrics = {"bleu": {}, "style": {}}
    bleu_files = [
        "results/metrics/t5_small_bleu.json",
        "results/metrics/hinglish_bleu.json",
        "results/metrics/forward_bleu.json",
        "results/metrics/reverse_bleu.json",
        "results/metrics/hinglish_forward_bleu.json",
        "results/metrics/hinglish_reverse_bleu.json",
    ]
    bleu_files.extend(glob.glob(os.path.join("results", "metrics", "*bleu*.json")))
    for bf in bleu_files:
        try:
            with open(bf, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    for label, payload in data.items():
                        if isinstance(payload, dict) and "bleu_score" in payload:
                            metrics["bleu"][label] = payload
        except Exception:
            continue
    sacre_paths = [
        os.path.join("results", "metrics", "sacrebleu_forward.json"),
        os.path.join("results", "metrics", "sacrebleu_reverse.json"),
    ]
    for sp in sacre_paths:
        try:
            if os.path.exists(sp):
                with open(sp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    val = data.get("corpus_bleu")
                    if isinstance(val, (int, float)):
                        lbl = "forward_test" if "forward" in os.path.basename(sp) else "reverse_test"
                        metrics["bleu"][lbl] = {"bleu_score": float(val)}
        except Exception:
            pass
    style_path = os.path.join("results", "metrics", "style_metrics.json")
    if os.path.exists(style_path):
        try:
            with open(style_path, "r", encoding="utf-8") as f:
                metrics["style"] = json.load(f)
        except Exception:
            metrics["style"] = {}
    return metrics

def pick_bleu_scores(bleu_dict):
    if not isinstance(bleu_dict, dict):
        return None, None
    def score(lbl):
        payload = bleu_dict.get(lbl)
        if isinstance(payload, dict):
            val = payload.get("bleu_score")
            return val if isinstance(val, (int, float)) else None
        return None
    forward_labels = ["forward_test", "hinglish_forward_test", "forward", "hinglish_forward_val", "forward_val"]
    reverse_labels = ["reverse_test", "hinglish_reverse_test", "reverse", "hinglish_reverse_val", "reverse_val", "reverse_val_baseline"]
    f_bleu = None
    r_bleu = None
    for lbl in forward_labels:
        val = score(lbl)
        if val is not None:
            f_bleu = val
            break
    for lbl in reverse_labels:
        val = score(lbl)
        if val is not None:
            r_bleu = val
            break
    return f_bleu, r_bleu

def summarize_style(style_dict):
    if not isinstance(style_dict, dict) or not style_dict:
        return None, None
    emojis = []
    slangs = []
    for _label, data in style_dict.items():
        if not isinstance(data, dict):
            continue
        e = data.get("emoji_presence")
        s = data.get("slang_presence")
        if isinstance(e, (int, float)):
            emojis.append(e)
        if isinstance(s, (int, float)):
            slangs.append(s)
    emoji_avg = sum(emojis) / len(emojis) if emojis else None
    slang_avg = sum(slangs) / len(slangs) if slangs else None
    return emoji_avg, slang_avg

@st.cache_resource
def load_model(local_dir=None, hf_id=None, fallback=FALLBACK_MODEL):
    if isinstance(local_dir, str) and os.path.isdir(local_dir):
        try:
            model = T5ForConditionalGeneration.from_pretrained(local_dir)
            tokenizer = T5TokenizerFast.from_pretrained(local_dir)
            return model, tokenizer, True
        except Exception:
            pass
    if isinstance(hf_id, str) and len(hf_id) > 0:
        try:
            kw = {}
            if HF_TOKEN:
                kw["token"] = HF_TOKEN
            model = T5ForConditionalGeneration.from_pretrained(hf_id, **kw)
            tokenizer = T5TokenizerFast.from_pretrained(hf_id, **kw)
            return model, tokenizer, True
        except Exception:
            pass
    model = T5ForConditionalGeneration.from_pretrained(fallback)
    tokenizer = T5TokenizerFast.from_pretrained(fallback)
    return model, tokenizer, False

def translate_text(text, model, tokenizer, max_source_len=MAX_SOURCE_LEN, max_target_len=MAX_TARGET_LEN):
    inputs = tokenizer(text, return_tensors="pt", max_length=max_source_len, padding="max_length", truncation=True)
    input_ids = inputs.input_ids.to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            max_length=max_target_len,
            num_beams=6,
            no_repeat_ngram_size=3,
            length_penalty=1.0,
            early_stopping=True,
            do_sample=False
        )
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return translated_text

# --- UI Component ---
def render_translation_ui(language, direction, model_path, model_id, use_prefix, style):
    model, tokenizer, is_finetuned = load_model(model_path, model_id, fallback=FALLBACK_MODEL)
    
    if not is_finetuned and "Hinglish" in language:
         st.warning(f"⚠️ Using fallback model. Specific {language} model not found.")

    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### 📥 Input")
        st.markdown("<div style='background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; padding:12px; box-shadow:0 2px 8px rgba(0,0,0,0.04);'>", unsafe_allow_html=True)
        
        # Load example text
        example_text = ""
        try:
            test_file = os.path.join("outputs", "data", "test.csv")
            if os.path.exists(test_file):
                with open(test_file, newline="", encoding="utf-8") as f:
                    r = csv.reader(f)
                    rows = list(r)
                    relevant_rows = []
                    for row in rows:
                        if len(row) >= 3 and row[2].strip().lower() == language.lower():
                            if direction == "forward":
                                relevant_rows.append(row[0])
                            else:
                                relevant_rows.append(row[1])
                    if relevant_rows:
                        example_text = random.choice(relevant_rows)
        except Exception:
            pass

        key_base = f"{language}_{direction}"
        input_key = f"{key_base}_input"
        
        # Toolbar for input
        ic1, ic2 = st.columns([1, 1])
        with ic1:
             st.caption("Enter text below:")
        with ic2:
            if st.button("🎲 Random Example", key=f"{key_base}_ex_btn", help="Load a random example from test set"):
                st.session_state[input_key] = example_text
            
        source_text = st.text_area(
            label="Input",
            label_visibility="visible",
            height=240,
            placeholder="Type your text here… (slang, memes, Hinglish)",
            key=input_key
        )
        
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        if not source_text or not source_text.strip():
            st.markdown("<div class='cta-disabled'>", unsafe_allow_html=True)
            translate_btn = st.button("⚡ Translate", key=f"{key_base}_run", type="primary", help="Enter text to enable")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            translate_btn = st.button("⚡ Translate", key=f"{key_base}_run", type="primary")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("### 📤 Output")
        st.markdown("<div style='background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; padding:12px; box-shadow:0 2px 8px rgba(0,0,0,0.04);'>", unsafe_allow_html=True)
        st.caption("Translation result:")
        output_placeholder = st.empty()
        
        # Initial empty state
        output_placeholder.text_area(label="Output", label_visibility="visible", height=260, disabled=True, value="", placeholder="Your translated text will appear here", key=f"{key_base}_output")

        if translate_btn:
            if source_text:
                output_placeholder.markdown("<div class='skeleton'></div>", unsafe_allow_html=True)
                with st.spinner("Translating…"):
                    src = source_text
                    if use_prefix:
                        src = f"{build_prefix(language, direction, style)} {src}".strip()
                    translated = translate_text(src, model, tokenizer)
                    output_placeholder.text_area(
                        label="Output", 
                        label_visibility="visible", 
                        height=260, 
                        value=translated,
                        key=f"{key_base}_output_result"
                    )
                    st.toast("Translation completed!", icon="✅")
            else:
                st.warning("Please enter some text to translate.")
        st.markdown("</div>", unsafe_allow_html=True)

def render_home():
    st.markdown("""
        <style>
        .home-hero {
            background: linear-gradient(135deg, #F8FAFC 0%, #EEF2F7 100%);
            border: 1px solid #e5e7eb;
            border-radius: 20px;
            padding: 48px 40px;
            box-shadow: 0 18px 42px rgba(17,24,39,0.10);
            position: relative;
            overflow: hidden;
            animation: fadeUp 640ms ease-out both;
        }
        .home-hero::before {
            content: "";
            position: absolute; right: -120px; top: -140px; width: 380px; height: 380px;
            background: radial-gradient(closest-side, rgba(99,102,241,0.20), rgba(16,185,129,0.12));
            filter: blur(42px); border-radius: 50%; animation: float 10s ease-in-out infinite;
        }
        .home-hero h1 {
            margin: 0; color: #111827; font-size: 2.6rem; font-weight: 800; letter-spacing: -0.02em;
        }
        .home-hero p {
            margin: 10px 0 22px; color: #475569; font-size: 1.08rem; font-weight: 600;
        }
        .cta-row { display:flex; gap:12px; align-items:center; }
        .cta {
            display:inline-flex; align-items:center; justify-content:center; padding: 14px 18px; border-radius: 12px; text-decoration:none; font-weight:800;
        }
        .cta-primary { background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%); color:#fff; box-shadow: 0 12px 26px rgba(79,70,229,0.35); }
        .cta-primary:hover { transform: translateY(-1px); box-shadow: 0 16px 30px rgba(79,70,229,0.45); }
        .cta-secondary { background:#fff; border:1px solid #e5e7eb; color:#334155; box-shadow:0 8px 18px rgba(17,24,39,0.06); }
        .cta-secondary:hover { border-color:#818CF8; transform: translateY(-1px); }
        .chips { display:flex; gap:10px; margin-top:12px; }
        .pill { display:inline-flex; padding:6px 10px; border-radius:999px; background:#ECFDF5; color:#065F46; font-weight:700; border:1px solid #10B981; }
        @keyframes float { 0% { transform: translateY(0)} 50% { transform: translateY(18px)} 100% { transform: translateY(0)} }
        @keyframes fadeUp { 0% { opacity:0; transform: translateY(12px)} 100% { opacity:1; transform: translateY(0)} }
        .feature-grid { margin-top: 26px; display:grid; grid-template-columns: repeat(3, 1fr); gap:18px; }
        .feature-card { background:#fff; border:1px solid #e5e7eb; border-radius:16px; padding:18px; box-shadow:0 10px 24px rgba(17,24,39,0.08); transition: all 220ms ease; }
        .feature-card:hover { transform: translateY(-3px); box-shadow: 0 14px 32px rgba(17,24,39,0.12); }
        .feature-card h3 { margin:6px 0 6px; color:#111827; font-size:1.05rem; font-weight:800; }
        .feature-card p { margin:0; color:#475569; font-size:0.95rem; }
        .preview { margin-top:18px; display:grid; grid-template-columns: 1.05fr 0.95fr; gap:16px; }
        .bubble { background:#fff; border:1px solid #e5e7eb; border-radius:16px; padding:14px; box-shadow:0 10px 24px rgba(17,24,39,0.08); }
        .bubble h4 { margin:0 0 8px; color:#111827; font-weight:800; }
        .bubble .text { color:#1f2937; font-weight:700; }
        .bubble .sub { color:#64748b; font-weight:600; }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("""
        <section class="home-hero">
            <div class="chip">✨ Slang & Meme Translator</div>
            <h1>Understand internet slang, memes, and Gen‑Z language instantly using AI.</h1>
            <p>Translate casual posts, comments, and Hinglish code‑mix into clear, professional English — and back again.</p>
            <div class="cta-row">
                <a class="cta cta-primary" href="#" onclick="return false;">⚡ Try the Translator</a>
                <a class="cta cta-secondary" href="https://github.com/neeraj214/cross-language-meme-slang-translator" target="_blank">View on GitHub</a>
            </div>
            <div class="chips">
                <div class="pill">Built on T5</div>
                <div class="pill">Hinglish support</div>
                <div class="pill">BLEU‑validated</div>
            </div>
        </section>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.markdown("<div class='feature-card'>🕵️‍♂️<h3>Slang Detection</h3><p>Emoji, abbreviations, and informal phrases recognized.</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='feature-card'>🧠<h3>Meme Context</h3><p>Preserves tone and humor with context awareness.</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='feature-card'>🌐<h3>Multi‑Language</h3><p>Handles English and Hinglish code‑mix seamlessly.</p></div>", unsafe_allow_html=True)
    ex_src, ex_tgt = random.choice([
        ("bro’s cooked 💀", "he messed up badly."),
        ("that fit is fire 🔥", "the outfit looks amazing."),
        ("yaar mood off ho gaya 😒", "i’m not in a good mood."),
        ("ain’t no way 😭", "i can’t believe this."),
    ])
    st.markdown(f"""
        <div class="preview">
            <div class="bubble"><h4>Slang</h4><div class="text">{ex_src}</div><div class="sub">sample input</div></div>
            <div class="bubble"><h4>Meaning</h4><div class="text">{ex_tgt}</div><div class="sub">interpreted output</div></div>
        </div>
    """, unsafe_allow_html=True)
    try_btn = st.button("⚡ Try the Translator", type="primary", key="home_try_cta")
    if try_btn:
        st.session_state["show_translator"] = True
        try:
            st.experimental_rerun()
        except Exception:
            pass

# --- Main App ---
def main():
    if not st.session_state.get("show_translator", False):
        render_home()
        return
    # Sidebar: Modern Config Panel (card-based layout for clarity and hierarchy)
    st.sidebar.title("🛠️ Config")
    st.sidebar.markdown(
        "<div style='background: #ffffff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 20px; box-shadow: 0 8px 24px rgba(17,24,39,0.06); margin-bottom: 16px;'>"
        "<div style='font-weight:800; color:#111827; margin-bottom:10px;'>Configuration</div>"
        "<div style='color:#6b7280; font-size:0.95rem; margin-bottom:14px;'>Set your language pair and translation style. These preferences guide how outputs are generated.</div>",
        unsafe_allow_html=True
    )
    language = st.sidebar.radio(
        "Language Pair",
        ["English", "Hinglish"],
        help="Choose between English-only translations or English↔Hinglish code-mixed translations."
    )
    style = st.sidebar.selectbox(
        "Translation Style",
        ["Neutral", "Casual", "Meme-heavy"],
        index=0,
        help="Neutral keeps tone formal; Casual adds informality; Meme-heavy preserves meme/slang context."
    )
    use_prefix = st.sidebar.checkbox(
        "Use Task Prefix",
        value=APPLY_TASK_PREFIX,
        help="Adds an instruction prefix to the model input for more consistent outputs."
    )
    st.sidebar.markdown(
        "<div style='border-top:1px dashed #e5e7eb; margin:16px 0;'></div>"
        "<div style='color:#6b7280; font-size:0.9rem;'>Tip: Switch language pairs via tabs in the main area for faster workflow.</div>"
        "</div>",
        unsafe_allow_html=True
    )
    
    # 2. Metrics Dashboard in Sidebar
    st.sidebar.title("📊 Metrics")
    metrics = load_metrics()
    f_bleu, r_bleu = pick_bleu_scores(metrics.get("bleu", {}))
    emoji_avg, slang_avg = summarize_style(metrics.get("style", {}))
    
    # Custom Card HTML for Sidebar
    def metric_card(label, value, icon=""):
        tooltip = "BLEU measures similarity to reference translations; higher is better."
        st.sidebar.markdown(f"""
        <div style="background: white; padding: 14px; border-radius: 12px; border: 1px solid #e5e7eb; margin-bottom: 10px; box-shadow: 0 6px 18px rgba(17,24,39,0.06);" title="{tooltip}">
            <div style="font-size: 0.85rem; color: #6b7280; display:flex; align-items:center; gap:6px;">
                <span>{icon}</span><span>{label}</span><span style="color:#818CF8;" title="{tooltip}">ⓘ</span>
            </div>
            <div style="font-size: 1.4rem; font-weight: 800; color: #10B981;">{value}</div>
        </div>
        """, unsafe_allow_html=True)

    st.sidebar.caption("BLEU Scores (Accuracy)")
    col_a, col_b = st.sidebar.columns(2)
    with col_a:
        val = f"{f_bleu:.2f}" if isinstance(f_bleu, (int, float)) else "—"
        metric_card("Forward", val, "➡️")
    with col_b:
        val = f"{r_bleu:.2f}" if isinstance(r_bleu, (int, float)) else "—"
        metric_card("Reverse", val, "⬅️")

    st.sidebar.caption("Style Analysis")
    col_c, col_d = st.sidebar.columns(2)
    with col_c:
        val = f"{emoji_avg:.2f}" if isinstance(emoji_avg, (int, float)) else "—"
        metric_card("Emoji %", val, "😀")
    with col_d:
        val = f"{slang_avg:.2f}" if isinstance(slang_avg, (int, float)) else "—"
        metric_card("Slang %", val, "💬")

    # Main Content Area
    st.markdown(
        """
        <section style="background: linear-gradient(135deg, #F8FAFC 0%, #EEF2F7 100%); padding: 24px; border-radius: 16px; border: 1px solid #e5e7eb; margin: 8px 0 24px;">
            <div style="display:flex; align-items:center; gap:14px;">
                <div style="background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%); color:white; width:40px; height:40px; display:flex; align-items:center; justify-content:center; border-radius:12px; font-weight:800; box-shadow: 0 6px 16px rgba(79,70,229,0.25);">AI</div>
                <div>
                    <h1 style="margin:0; color:#111827; font-size:2.1rem; font-weight:800; letter-spacing:-0.02em;">🔁 Slang/Meme Translator</h1>
                    <p style="margin:6px 0 0; color:#6b7280; font-size:1rem;">Translate internet slang, memes, and Hinglish with controllable tone and clear outputs.</p>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )
    
    if language == "English":
        tab1, tab2 = st.tabs(["🇺🇸 Slang ➡️ English", "🇺🇸 English ➡️ Slang"])
        with tab1:
            render_translation_ui("English", "forward", FORWARD_MODEL_PATH, FORWARD_MODEL_ID, use_prefix, style)
        with tab2:
            render_translation_ui("English", "reverse", REVERSE_MODEL_PATH, REVERSE_MODEL_ID, use_prefix, style)
    
    else:  # Hinglish
        tab1, tab2 = st.tabs(["🇮🇳 Hinglish ➡️ English", "🇮🇳 English ➡️ Hinglish"])
        with tab1:
            render_translation_ui("Hinglish", "forward", HINGLISH_FORWARD_MODEL_PATH, HINGLISH_FORWARD_MODEL_ID, use_prefix, style)
        with tab2:
            render_translation_ui("Hinglish", "reverse", HINGLISH_REVERSE_MODEL_PATH, HINGLISH_REVERSE_MODEL_ID, use_prefix, style)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #888; font-size: 0.8rem;'>Built with ❤️ using T5 & Streamlit</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
