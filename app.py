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

# Custom CSS for Premium Modern Look
def local_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@400;600;700&display=swap');

        :root {
            --primary: #6366F1;
            --primary-glow: rgba(99, 102, 241, 0.25);
            --secondary: #10B981;
            --bg-surface: #FFFFFF;
            --bg-page: #F8FAFC;
            --glass-bg: rgba(255, 255, 255, 0.9);
            --glass-border: #E2E8F0;
            --text-main: #020617;
            --text-muted: #475569;
        }

        .stApp {
            background-color: var(--bg-page);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
        }

        h1, h2, h3, .brand-text {
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
        }

        .glass-card {
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
        }

        [data-testid="stSidebar"] {
            background-color: rgba(255, 255, 255, 0.92);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-right: 1px solid #E2E8F0;
        }

        .stTextArea textarea {
            background: #FFFFFF !important;
            color: #020617 !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            font-family: 'Inter', sans-serif !important;
        }
        .stTextArea textarea::placeholder {
            color: #9CA3AF !important;
        }

        .stTextArea textarea:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px var(--primary-glow) !important;
        }

        .stButton>button {
            border-radius: 12px;
            font-weight: 700;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
            border: none;
            color: white;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }

        .stButton>button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
        }

        [data-testid="stMetric"] {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            padding: 15px;
            border-radius: 16px;
            text-align: center;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background-color: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: var(--glass-bg);
            border-radius: 12px 12px 0 0;
            padding: 10px 20px;
            color: var(--text-muted);
        }

        .stTabs [aria-selected="true"] {
            color: var(--primary) !important;
            background-color: rgba(99, 102, 241, 0.1) !important;
            border-bottom: 2px solid var(--primary) !important;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .animate-fade-in {
            animation: fadeIn 0.8s ease-out forwards;
        }

        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: #CBD5E1;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #94A3B8;
        }

        .output-box {
            background: #FFFFFF;
            border-radius: 12px;
            border: 1px solid #E2E8F0;
            padding: 16px 18px;
            font-size: 1rem;
            color: var(--text-main);
            line-height: 1.6;
        }

        .copy-btn {
            border-radius: 999px;
            padding: 6px 14px;
            border: 1px solid #E2E8F0;
            background: #F9FAFB;
            font-size: 0.75rem;
            font-weight: 600;
            color: #0F172A;
            cursor: pointer;
            transition: background 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
        }
        .copy-btn:hover {
            background: #EEF2FF;
            box-shadow: 0 4px 10px rgba(99, 102, 241, 0.18);
            transform: translateY(-1px);
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
        os.path.join("results", "metrics", "sacrebleu_forward_rich_raw.json"),
        os.path.join("results", "metrics", "sacrebleu_forward_rich_norm.json"),
    ]
    for sp in sacre_paths:
        try:
            if os.path.exists(sp):
                with open(sp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    val = data.get("corpus_bleu")
                    if isinstance(val, (int, float)):
                        base = os.path.basename(sp)
                        if "reverse" in base:
                            lbl = "reverse_test"
                        elif "rich_raw" in base:
                            lbl = "forward_rich_raw"
                        elif "rich_norm" in base:
                            lbl = "forward_rich_norm"
                        else:
                            lbl = "forward_test"
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
        st.markdown("<div class='glass-card animate-fade-in'>", unsafe_allow_html=True)
        st.markdown(f"### 📥 Input ({language})")
        
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
        
        source_text = st.text_area(
            label="Translate from:",
            height=200,
            placeholder="Type your text here... (e.g. 'this fit is fire 🔥')",
            key=input_key
        )
        
        ic1, ic2 = st.columns([1, 1])
        with ic1:
            if st.button("🎲 Random Example", key=f"{key_base}_ex_btn", help="Load sample text"):
                st.session_state[input_key] = example_text
                st.rerun()
        with ic2:
            translate_btn = st.button("⚡ Translate", key=f"{key_base}_run", type="primary", use_container_width=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card animate-fade-in' style='transition-delay: 0.1s;'>", unsafe_allow_html=True)
        st.markdown("### 📤 Translation")
        output_placeholder = st.empty()
        if translate_btn and source_text:
            with st.spinner("Decoding slang..."):
                src = source_text
                if use_prefix:
                    src = f"{build_prefix(language, direction, style)} {src}".strip()
                translated = translate_text(src, model, tokenizer)
                safe_key = key_base.replace(" ", "_").lower()
                output_placeholder.markdown(
                    f"""
                    <div id="{safe_key}_output" class="output-box">{translated}</div>
                    <div style="margin-top:8px; display:flex; justify-content:flex-end;">
                        <button class="copy-btn" id="{safe_key}_copy">Copy translation</button>
                    </div>
                    <script>
                    const btn_{safe_key} = document.getElementById("{safe_key}_copy");
                    const out_{safe_key} = document.getElementById("{safe_key}_output");
                    if (btn_{safe_key} && out_{safe_key}) {{
                        btn_{safe_key}.onclick = async () => {{
                            try {{
                                await navigator.clipboard.writeText(out_{safe_key}.innerText);
                                btn_{safe_key}.innerText = "Copied";
                                setTimeout(() => (btn_{safe_key}.innerText = "Copy translation"), 1600);
                            }} catch (e) {{}}
                        }};
                    }}
                    </script>
                    """,
                    unsafe_allow_html=True,
                )
                st.toast("Translation copied-ready ✨", icon="✨")
        else:
            output_placeholder.info("Translation will appear here after clicking 'Translate'")
        st.markdown("</div>", unsafe_allow_html=True)

def render_home():
    st.markdown("""
        <div class="animate-fade-in" style="text-align: center; padding: 40px 20px;">
            <div style="display: inline-block; padding: 8px 16px; border-radius: 99px; background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); color: #818CF8; font-weight: 700; font-size: 0.85rem; margin-bottom: 24px; letter-spacing: 1px; text-transform: uppercase;">
                ✨ The Future of Slang Translation
            </div>
            <h1 style="font-size: 3.5rem; line-height: 1.1; margin-bottom: 24px; background: linear-gradient(135deg, #F8FAFC 0%, #CBD5E1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Decipher the Internet.<br>Master the Meme.
            </h1>
            <p style="font-size: 1.25rem; color: #94A3B8; max-width: 700px; margin: 0 auto 40px; line-height: 1.6;">
                Bridge the gap between internet slang, memes, and standard English using our fine-tuned AI. Seamlessly translate across English and Hinglish.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="glass-card animate-fade-in" style="height: 100%;">
                <div style="font-size: 2rem; margin-bottom: 16px;">🕵️‍♂️</div>
                <h3 style="color: #F8FAFC; margin-bottom: 12px;">Slang Detection</h3>
                <p style="color: #94A3B8; font-size: 0.95rem;">emoji, abbreviations, and informal phrases recognized with high precision.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="glass-card animate-fade-in" style="height: 100%; transition-delay: 0.1s;">
                <div style="font-size: 2rem; margin-bottom: 16px;">🧠</div>
                <h3 style="color: #F8FAFC; margin-bottom: 12px;">Meme Context</h3>
                <p style="color: #94A3B8; font-size: 0.95rem;">Preserves humor and nuance across cultural contexts and internet trends.</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="glass-card animate-fade-in" style="height: 100%; transition-delay: 0.2s;">
                <div style="font-size: 2rem; margin-bottom: 16px;">🌐</div>
                <h3 style="color: #F8FAFC; margin-bottom: 12px;">Multi-Language</h3>
                <p style="color: #94A3B8; font-size: 0.95rem;">Native support for Hinglish code-mixing and regional slang patterns.</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 48px;'></div>", unsafe_allow_html=True)

    # Preview Section
    preview_col1, preview_col2 = st.columns([1, 1])
    with preview_col1:
        st.markdown("<div style='color: #F8FAFC; font-weight: 700; margin-bottom: 12px;'>Example Input</div>", unsafe_allow_html=True)
        st.code("bro's cooked 💀 he really thought he ate with that fit.", language=None)
    with preview_col2:
        st.markdown("<div style='color: #10B981; font-weight: 700; margin-bottom: 12px;'>AI Translation</div>", unsafe_allow_html=True)
        st.code("He is in a very bad situation. He mistakenly believed his outfit looked good.", language=None)

    st.markdown("<div style='margin-bottom: 48px;'></div>", unsafe_allow_html=True)
    
    # CTA
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🚀 Enter Translator", type="primary", use_container_width=True):
            st.session_state["show_translator"] = True
            st.rerun()

# --- Main App ---
def main():
    if not st.session_state.get("show_translator", False):
        render_home()
        return
    st.sidebar.markdown(f"""
        <div class="glass-card" style="margin-bottom: 24px;">
            <h2 style="margin:0; color:var(--text-main); font-size:1.5rem;">🛠️ Settings</h2>
            <p style="color:var(--text-muted); font-size:0.9rem; margin-top:8px;">Configure the model and translation style.</p>
        </div>
    """, unsafe_allow_html=True)
    
    language = st.sidebar.radio(
        "Language Pair",
        ["English", "Hinglish"],
        help="Choose between English-only or English↔Hinglish."
    )
    style = st.sidebar.selectbox(
        "Translation Style",
        ["Neutral", "Casual", "Meme-heavy"],
        index=0,
    )
    use_prefix = st.sidebar.checkbox(
        "Use Task Prefix",
        value=APPLY_TASK_PREFIX,
    )

    show_metrics = st.sidebar.toggle(
        "Show developer metrics",
        value=False,
        help="Enable BLEU and style metrics for model evaluation.",
    )
    if show_metrics:
        st.sidebar.markdown("<br>", unsafe_allow_html=True)
        st.sidebar.markdown("<h2 style='font-size:1.2rem; margin-bottom:12px;'>📊 Performance</h2>", unsafe_allow_html=True)
        metrics = load_metrics()
        f_bleu, r_bleu = pick_bleu_scores(metrics.get("bleu", {}))
        emoji_avg, slang_avg = summarize_style(metrics.get("style", {}))
        m_col1, m_col2 = st.sidebar.columns(2)
        with m_col1:
            st.metric("Forward BLEU", f"{f_bleu:.1f}" if f_bleu else "N/A")
        with m_col2:
            st.metric("Reverse BLEU", f"{r_bleu:.1f}" if r_bleu else "N/A")

    # Main Content Area
    st.markdown(
        f"""
        <div class="animate-fade-in" style="margin-bottom: 32px;">
            <div style="display:flex; align-items:center; gap:16px;">
                <div style="background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%); color:white; width:48px; height:48px; display:flex; align-items:center; justify-content:center; border-radius:14px; font-weight:800; font-size:1.2rem; box-shadow: 0 8px 16px rgba(99,102,241,0.3);">AI</div>
                <div>
                    <h1 style="margin:0; font-size:2.2rem;">Translator Lab</h1>
                    <p style="margin:0; color:var(--text-muted);">Current Mode: {language} ({style} style)</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if language == "English":
        tab1, tab2 = st.tabs(["🇺🇸 Slang ➡️ Std English", "🇺🇸 Std English ➡️ Slang"])
        with tab1:
            render_translation_ui("English", "forward", FORWARD_MODEL_PATH, FORWARD_MODEL_ID, use_prefix, style)
        with tab2:
            render_translation_ui("English", "reverse", REVERSE_MODEL_PATH, REVERSE_MODEL_ID, use_prefix, style)
    
    else:  # Hinglish
        tab1, tab2 = st.tabs(["🇮🇳 Hinglish ➡️ Std English", "🇮🇳 Std English ➡️ Hinglish"])
        with tab1:
            render_translation_ui("Hinglish", "forward", HINGLISH_FORWARD_MODEL_PATH, HINGLISH_FORWARD_MODEL_ID, use_prefix, style)
        with tab2:
            render_translation_ui("Hinglish", "reverse", HINGLISH_REVERSE_MODEL_PATH, HINGLISH_REVERSE_MODEL_ID, use_prefix, style)

    # Footer
    st.markdown("<div style='margin-bottom: 60px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align: center; padding: 24px; border-top: 1px solid var(--glass-border);'>
            <p style='color: var(--text-muted); font-size: 0.9rem;'>
                Built with ❤️ using <b>FLAN-T5</b> & <b>Streamlit</b> • MCA Semester 1 NLP Project
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
