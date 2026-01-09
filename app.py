import streamlit as st
import torch
from transformers import T5ForConditionalGeneration, T5TokenizerFast
import os
import json
import glob

# Set page configuration
st.set_page_config(
    page_title="Slang/Meme Translator",
    page_icon="🔁",
    layout="wide",
    initial_sidebar_state="expanded"
)

FORWARD_MODEL_PATH = os.environ.get("FORWARD_MODEL", "outputs/checkpoints/t5-small-forward-ep5-lr3e4-64")
REVERSE_MODEL_PATH = os.environ.get("REVERSE_MODEL", "outputs/checkpoints/t5-small-reverse-ep5-lr3e4-64")
HINGLISH_FORWARD_MODEL_PATH = os.environ.get("HINGLISH_FORWARD_MODEL", "outputs/checkpoints/t5-small-hinglish-forward-ep10-lr0.0002-64")
HINGLISH_REVERSE_MODEL_PATH = os.environ.get("HINGLISH_REVERSE_MODEL", "outputs/checkpoints/t5-small-hinglish-reverse-ep10-lr0.0002-64")
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
def load_model(model_id, fallback=FALLBACK_MODEL):
    if isinstance(model_id, str) and os.path.isdir(model_id):
        try:
            model = T5ForConditionalGeneration.from_pretrained(model_id)
            tokenizer = T5TokenizerFast.from_pretrained(model_id)
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
    # Minimal, modern header
    st.title("Slang/Meme Translator")
    st.caption("Translate between slang/meme text and standard English or Hinglish.")
    
    # Load metrics
    metrics = load_metrics()
    
    # Sidebar with metrics
    st.sidebar.title("Model Performance")
    # Pick concise metrics
    f_bleu, r_bleu = pick_bleu_scores(metrics.get("bleu", {}))
    emoji_avg, slang_avg = summarize_style(metrics.get("style", {}))

    perf = st.sidebar.container()
    c1, c2 = perf.columns(2)
    # BLEU cards
    if isinstance(f_bleu, (int, float)):
        c1.metric("Forward BLEU", f"{f_bleu:.2f}")
    else:
        c1.metric("Forward BLEU", "—")
    if isinstance(r_bleu, (int, float)):
        c2.metric("Reverse BLEU", f"{r_bleu:.2f}")
    else:
        c2.metric("Reverse BLEU", "—")

    c3, c4 = perf.columns(2)
    # Style cards
    if isinstance(emoji_avg, (int, float)):
        c3.metric("Emoji Presence", f"{emoji_avg:.2f}")
    else:
        c3.metric("Emoji Presence", "—")
    if isinstance(slang_avg, (int, float)):
        c4.metric("Slang Presence", f"{slang_avg:.2f}")
    else:
        c4.metric("Slang Presence", "—")
    
    # Language selection
    # Modernized controls
    language = st.radio("Language", ["English", "Hinglish"], horizontal=True)
    st.sidebar.subheader("Controls")
    use_prefix = st.sidebar.checkbox("Use task prefix", value=APPLY_TASK_PREFIX)
    style = st.sidebar.selectbox("Output style", ["Neutral", "Casual", "Meme-heavy"], index=0)
    
    # Main content
    # Use tabs to reduce visual clutter
    if language == "English":
        tab1, tab2 = st.tabs(["Slang → English", "English → Slang"])
        
        with tab1:
            st.subheader("English Slang/Meme → Standard English")
            forward_model, forward_tokenizer, is_forward_finetuned = load_model(FORWARD_MODEL_PATH)
            
            source_text = st.text_area(
                "Enter English slang/meme text:",
                height=150,
                placeholder="Type your English slang or meme text here...",
                key="english_slang_input"
            )
            
            if st.button("Translate", key="english_forward_btn"):
                if source_text:
                    with st.spinner("Translating..."):
                        src = source_text
                        if use_prefix:
                            src = f"{build_prefix('English', 'forward', style)} {src}".strip()
                        translated = translate_text(src, forward_model, forward_tokenizer)
                        st.success("Translation complete!")
                        st.text_area("Translation", translated, height=120)
                else:
                    st.warning("Please enter some text to translate")
        
        with tab2:
            st.subheader("Standard English → English Slang/Meme")
            reverse_model, reverse_tokenizer, is_reverse_finetuned = load_model(REVERSE_MODEL_PATH)
            
            target_text = st.text_area(
                "Enter standard English text:",
                height=150,
                placeholder="Type your standard English text here...",
                key="english_input"
            )
            
            if st.button("Translate", key="english_reverse_btn"):
                if target_text:
                    with st.spinner("Translating..."):
                        tgt = target_text
                        if use_prefix:
                            tgt = f"{build_prefix('English', 'reverse', style)} {tgt}".strip()
                        translated = translate_text(tgt, reverse_model, reverse_tokenizer)
                        st.success("Translation complete!")
                        st.text_area("Translation", translated, height=120)
                else:
                    st.warning("Please enter some text to translate")
    
    else:  # Hinglish
        tab1, tab2 = st.tabs(["Hinglish → English", "English → Hinglish"])
        
        with tab1:
            st.subheader("Hinglish Slang/Meme → Standard English")
            hinglish_forward_model, hinglish_forward_tokenizer, is_hinglish_forward_finetuned = load_model(
                HINGLISH_FORWARD_MODEL_PATH,
                fallback=FALLBACK_MODEL
            )
            
            source_text = st.text_area(
                "Enter Hinglish slang/meme text:",
                height=150,
                placeholder="Type your Hinglish slang or meme text here...",
                key="hinglish_slang_input"
            )
            
            if st.button("Translate", key="hinglish_forward_btn"):
                if source_text:
                    with st.spinner("Translating..."):
                        src = source_text
                        if use_prefix:
                            src = f"{build_prefix('Hinglish', 'forward', style)} {src}".strip()
                        translated = translate_text(src, hinglish_forward_model, hinglish_forward_tokenizer)
                        st.success("Translation complete!")
                        st.text_area("Translation", translated, height=120)
                        
                        if not is_hinglish_forward_finetuned:
                            st.info("Note: Using fallback model as Hinglish model is not yet trained. Results may not be optimal for Hinglish text.")
                else:
                    st.warning("Please enter some text to translate")
        
        with tab2:
            st.subheader("Standard English → Hinglish Slang/Meme")
            hinglish_reverse_model, hinglish_reverse_tokenizer, is_hinglish_reverse_finetuned = load_model(
                HINGLISH_REVERSE_MODEL_PATH,
                fallback=FALLBACK_MODEL
            )
            
            target_text = st.text_area(
                "Enter standard English text:",
                height=150,
                placeholder="Type your standard English text here...",
                key="hinglish_input"
            )
            
            if st.button("Translate", key="hinglish_reverse_btn"):
                if target_text:
                    with st.spinner("Translating..."):
                        tgt = target_text
                        if use_prefix:
                            tgt = f"{build_prefix('Hinglish', 'reverse', style)} {tgt}".strip()
                        translated = translate_text(tgt, hinglish_reverse_model, hinglish_reverse_tokenizer)
                        st.success("Translation complete!")
                        st.text_area("Translation", translated, height=120)
                        
                        if not is_hinglish_reverse_finetuned:
                            st.info("Note: Using fallback model as Hinglish model is not yet trained. Results may not be optimal for Hinglish output.")
            else:
                st.warning("Please enter some text to translate")

if __name__ == "__main__":
    main()
