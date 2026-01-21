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

# Custom CSS for better UI
def local_css():
    st.markdown("""
        <style>
        .stTextArea textarea {
            font-size: 16px !important;
            border-radius: 8px;
        }
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            height: 3em;
            font-weight: bold;
        }
        .reportview-container .main .block-container {
            padding-top: 2rem;
        }
        h1 {
            color: #4F8BF9;
            font-weight: 700;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            text-align: center;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

local_css()

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
APPLY_TASK_PREFIX = False  # toggle to prepend task hints at inference

def build_prefix(language: str, direction: str, style: str) -> str:
    # direction: 'forward' (slang->english) or 'reverse' (english->slang)
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

# Load metrics if available
def load_metrics():
    """Load BLEU and style metrics from results/metrics with robust fallbacks.

    BLEU: merges entries from any JSON containing a top-level object with
    keys that include 'bleu_score'. Supports files like:
    - hinglish_bleu.json
    - forward_bleu.json / reverse_bleu.json
    - t5_small_bleu.json

    Style: reads style_metrics.json when present.
    """
    metrics = {"bleu": {}, "style": {}}

    # Aggregate BLEU from all matching files
    bleu_files = [
        "results/metrics/t5_small_bleu.json",
        "results/metrics/hinglish_bleu.json",
        "results/metrics/forward_bleu.json",
        "results/metrics/reverse_bleu.json",
        "results/metrics/hinglish_forward_bleu.json",
        "results/metrics/hinglish_reverse_bleu.json",
    ]

    # Also pick up any other *_bleu.json files
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

    # Style metrics
    style_path = os.path.join("results", "metrics", "style_metrics.json")
    if os.path.exists(style_path):
        try:
            with open(style_path, "r", encoding="utf-8") as f:
                metrics["style"] = json.load(f)
        except Exception:
            metrics["style"] = {}

    return metrics


def pick_bleu_scores(bleu_dict):
    """Select concise BLEU metrics for display: Forward and Reverse.

    Priority order prefers test metrics, then validation, then generic labels.
    Returns (forward_bleu, reverse_bleu) or (None, None) when unavailable.
    """
    if not isinstance(bleu_dict, dict):
        return None, None

    def score(lbl):
        payload = bleu_dict.get(lbl)
        if isinstance(payload, dict):
            val = payload.get("bleu_score")
            return val if isinstance(val, (int, float)) else None
        return None

    forward_labels = [
        "forward_test",
        "hinglish_forward_test",
        "forward",
        "hinglish_forward_val",
        "forward_val",
    ]
    reverse_labels = [
        "reverse_test",
        "hinglish_reverse_test",
        "reverse",
        "hinglish_reverse_val",
        "reverse_val",
        "reverse_val_baseline",
    ]

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
    """Summarize style metrics to key values: emoji_presence and slang_presence.

    If multiple labels exist, compute simple averages over available numeric fields.
    Returns (emoji_presence, slang_presence) which may be None when missing.
    """
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

# Load model and tokenizer
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

# Translation function
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

# App UI
def main():
    # Header
    st.title("🔁 Slang/Meme Translator")
    st.markdown("### Translate between **Slang/Meme** text and **Standard English** or **Hinglish**.")
    st.markdown("---")
    
    # Load metrics
    metrics = load_metrics()
    
    # Sidebar with metrics
    st.sidebar.title("📊 Model Performance")
    st.sidebar.markdown("---")
    
    # Pick concise metrics
    f_bleu, r_bleu = pick_bleu_scores(metrics.get("bleu", {}))
    emoji_avg, slang_avg = summarize_style(metrics.get("style", {}))

    perf = st.sidebar.container()
    st.sidebar.subheader("BLEU Scores")
    c1, c2 = st.sidebar.columns(2)
    
    # BLEU cards
    if isinstance(f_bleu, (int, float)):
        c1.metric("Forward", f"{f_bleu:.2f}")
    else:
        c1.metric("Forward", "—")
    if isinstance(r_bleu, (int, float)):
        c2.metric("Reverse", f"{r_bleu:.2f}")
    else:
        c2.metric("Reverse", "—")

    st.sidebar.subheader("Style Metrics")
    c3, c4 = st.sidebar.columns(2)
    # Style cards
    if isinstance(emoji_avg, (int, float)):
        c3.metric("Emoji %", f"{emoji_avg:.2f}")
    else:
        c3.metric("Emoji %", "—")
    if isinstance(slang_avg, (int, float)):
        c4.metric("Slang %", f"{slang_avg:.2f}")
    else:
        c4.metric("Slang %", "—")
    
    st.sidebar.markdown("---")
    
    # Language selection
    st.sidebar.subheader("⚙️ Controls")
    language = st.sidebar.radio("Target Language Pair", ["English", "Hinglish"])
    use_prefix = st.sidebar.checkbox("Use task prefix", value=APPLY_TASK_PREFIX)
    style = st.sidebar.selectbox("Output style", ["Neutral", "Casual", "Meme-heavy"], index=0)
    
    # Main content
    if language == "English":
        tab1, tab2 = st.tabs(["🇺🇸 Slang → English", "🇺🇸 English → Slang"])
        
        with tab1:
            st.subheader("English Slang/Meme → Standard English")
            render_translation_ui("English", "forward", FORWARD_MODEL_PATH, FORWARD_MODEL_ID, use_prefix, style)
        
        with tab2:
            st.subheader("Standard English → English Slang/Meme")
            render_translation_ui("English", "reverse", REVERSE_MODEL_PATH, REVERSE_MODEL_ID, use_prefix, style)
    
    else:  # Hinglish
        tab1, tab2 = st.tabs(["🇮🇳 Hinglish → English", "🇮🇳 English → Hinglish"])
        
        with tab1:
            st.subheader("Hinglish Slang/Meme → Standard English")
            render_translation_ui("Hinglish", "forward", HINGLISH_FORWARD_MODEL_PATH, HINGLISH_FORWARD_MODEL_ID, use_prefix, style)
        
        with tab2:
            st.subheader("Standard English → Hinglish Slang/Meme")
            render_translation_ui("Hinglish", "reverse", HINGLISH_REVERSE_MODEL_PATH, HINGLISH_REVERSE_MODEL_ID, use_prefix, style)

def render_translation_ui(language, direction, model_path, model_id, use_prefix, style):
    """Reusable UI component for translation"""
    
    # Load model
    model, tokenizer, is_finetuned = load_model(model_path, model_id, fallback=FALLBACK_MODEL)
    
    if not is_finetuned and "Hinglish" in language:
         st.warning(f"Note: Using fallback model as {language} model is not yet trained/found.")

    # Layout: Input | Output
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Input Text**")
        
        # Example loader logic
        example_text = ""
        try:
            test_file = os.path.join("outputs", "data", "test.csv")
            if os.path.exists(test_file):
                with open(test_file, newline="", encoding="utf-8") as f:
                    r = csv.reader(f)
                    rows = list(r)
                    # Filter relevant rows
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
        
        if st.button("🎲 Use Random Example", key=f"{key_base}_ex_btn"):
            st.session_state[input_key] = example_text
            
        source_text = st.text_area(
            label="Input",
            label_visibility="collapsed",
            height=200,
            placeholder="Type here...",
            key=input_key
        )
        
        translate_btn = st.button("🚀 Translate", key=f"{key_base}_run", type="primary")

    with col2:
        st.markdown("**Translation**")
        output_placeholder = st.empty()
        output_placeholder.text_area(label="Output", label_visibility="collapsed", height=200, disabled=True, value="")

        if translate_btn:
            if source_text:
                with st.spinner("Translating..."):
                    src = source_text
                    if use_prefix:
                        src = f"{build_prefix(language, direction, style)} {src}".strip()
                    translated = translate_text(src, model, tokenizer)
                    output_placeholder.text_area(
                        label="Output", 
                        label_visibility="collapsed", 
                        height=200, 
                        value=translated
                    )
                    st.success("Done!")
            else:
                st.warning("Please enter some text to translate.")

if __name__ == "__main__":
    main()
