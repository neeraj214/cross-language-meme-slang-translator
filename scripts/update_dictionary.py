import os
import sys
import json
import re
import pandas as pd

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataset.slang_emoji_dict import EMOJI_DICT, ENGLISH_SLANG_DICT, HINGLISH_DICT

try:
    from emoji import EMOJI_DATA
except Exception:
    EMOJI_DATA = {}

STOPWORDS = set([
    # minimal stopwords to reduce noise
    'the','a','an','and','or','but','if','then','so','of','to','in','on','for','with','at','by','from','as','is','are','was','were','be','been','being','it','this','that','these','those','i','you','he','she','we','they','my','your','his','her','our','their','me','him','her','us','them'
])

def tokenize_words(text: str):
    if not isinstance(text, str):
        return []
    # Lowercase and extract word tokens
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text.lower())

def extract_emojis(text: str):
    if not isinstance(text, str):
        return []
    return [ch for ch in text if ch in EMOJI_DATA]

def update_dictionary():
    """Scan dataset for unknown slang/emojis and record placeholders in auto_updates.json."""
    # Dataset path
    dataset_xlsx = r"C:\Users\neera\OneDrive\Documents\NLP_Project\cleaned_slang_translations.xlsx"
    dataset_csv = r"C:\Users\neera\OneDrive\Documents\NLP_Project\cleaned_slang_translations.csv"

    # Load dataset
    df = None
    if os.path.exists(dataset_xlsx):
        df = pd.read_excel(dataset_xlsx)
    elif os.path.exists(dataset_csv):
        df = pd.read_csv(dataset_csv)
    else:
        print("❌ No dataset found. Expected Excel/CSV at the project root.")
        return

    # Prepare accumulators
    new_emojis = {}
    new_english = {}
    new_hinglish = {}

    # Iterate rows
    lang_col_present = 'Language' in df.columns
    text_col = 'Slang/Meme Text' if 'Slang/Meme Text' in df.columns else None
    if not text_col:
        print("❌ Column 'Slang/Meme Text' not found in dataset.")
        return

    for _, row in df.iterrows():
        text = row[text_col]
        lang = (row['Language'].lower() if lang_col_present and isinstance(row['Language'], str) else 'both')

        # emojis
        for e in extract_emojis(text):
            if e not in EMOJI_DICT:
                new_emojis[e] = new_emojis.get(e, 0) + 1

        # words
        for tok in tokenize_words(text):
            if tok in STOPWORDS:
                continue
            # known?
            is_known = tok in ENGLISH_SLANG_DICT or tok in HINGLISH_DICT
            if is_known:
                continue

            if lang == 'hinglish':
                new_hinglish[tok] = new_hinglish.get(tok, 0) + 1
            else:
                new_english[tok] = new_english.get(tok, 0) + 1

    # Build updates payload with placeholder meanings
    updates = {
        'EMOJI_DICT': {k: 'TODO: add meaning' for k in new_emojis.keys()},
        'ENGLISH_SLANG_DICT': {k: 'TODO: add meaning' for k in new_english.keys()},
        'HINGLISH_DICT': {k: 'TODO: add meaning' for k in new_hinglish.keys()},
    }

    # Load existing auto_updates and merge
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    updates_path = os.path.join(base_dir, 'dataset', 'auto_updates.json')

    existing = {'EMOJI_DICT': {}, 'ENGLISH_SLANG_DICT': {}, 'HINGLISH_DICT': {}}
    if os.path.exists(updates_path):
        try:
            with open(updates_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except Exception:
            pass

    # Merge new entries without overwriting existing
    for section in existing:
        existing[section].update({k: v for k, v in updates.get(section, {}).items() if k not in existing[section]})

    # Ensure directory exists
    os.makedirs(os.path.dirname(updates_path), exist_ok=True)

    # Write back
    with open(updates_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print("✅ Auto-updates written to:", updates_path)
    print(f"New emojis: {len(new_emojis)} | New English: {len(new_english)} | New Hinglish: {len(new_hinglish)}")

if __name__ == '__main__':
    update_dictionary()