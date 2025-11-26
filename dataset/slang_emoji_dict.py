"""
Slang and Emoji Dictionary for normalization
"""

import re
import os
import json

def _load_updates():
    """Load auto-updates from JSON if present."""
    try:
        base_dir = os.path.dirname(__file__)
        updates_path = os.path.join(base_dir, 'auto_updates.json')
        if os.path.exists(updates_path):
            with open(updates_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

# Emoji to text mapping
EMOJI_DICT = {
    "😂": "laughing hard",
    "🔥": "amazing", 
    "💯": "perfect",
    "😭": "crying",
    "🤣": "laughing very hard",
    "❤️": "love",
    "🙏": "thank you",
    "👍": "good",
    "👌": "excellent",
    "😍": "lovely",
    "😊": "happy",
    "🎉": "celebrating",
    "🤔": "thinking",
    "😎": "cool",
    "💀": "dying of laughter",
    "💔": "heartbroken",
    "✨": "sparkling",
    "🥺": "pleading",
    "🙄": "sarcastic",
    "🥵": "hot",
    "🥶": "cold",
    "😡": "angry",
    "🤮": "disgusting",
    "👀": "watching closely",
    # Curated additions
    "🍕": "pizza",
    "💪": "strong",
    "😬": "awkward",
    "🏆": "trophy",
    "🙅": "no",
    "🧠": "smart",
    "🍔": "burger",
    "🐐": "greatest of all time",
    "🎯": "on point",
    "👏": "applause",
    "🤨": "skeptical",
    "🧢": "lie",
    "😳": "embarrassed",
    "😒": "unimpressed",
    "😅": "nervous laugh",
    "🙌": "praise",
    "🤯": "mind blown",
    "🎧": "music",
    "🤳": "selfie",
    "💎": "precious",
    "🔝": "top",
    "🚩": "red flag",
    "💬": "message",
    "💡": "idea",
    "📈": "growth",
    "❤": "love",
    "💛": "love",
    "🎭": "drama",
    "📲": "phone",
    "😩": "exhausted",
    "😏": "smug",
    "⚡": "fast",
    "🏅": "medal",
    "💅": "confident",
    "🎤": "mic drop",
    "☕": "coffee",
    "👑": "royalty",
    "🌙": "night",
    "💸": "money",
    "🫶": "love",
    "😶": "speechless",
    "🫠": "overwhelmed",
    "🔎": "search",
    "😱": "shocked",
    "📺": "tv",
    "🚀": "skyrocketing",
    "🚫": "no",
    "🙃": "sarcastic",
    "😮": "surprised",
    "💨": "speed",
    "🕶": "cool",
    "🎢": "rollercoaster",
    "🐢": "slow",
    "🌟": "star",
    "😫": "tired",
    "✌": "peace",
    "🗑": "trash",
    "🔓": "unlock",
    "📚": "books",
    "😔": "sad",
    "🤷": "unsure",
    "💤": "sleep",
    "🎓": "graduate",
    "🍟": "fries",
    "⚠": "warning",
    "✅": "check",
    "🚨": "alarm",
    "🚧": "construction"
}

# English slang to standard English
ENGLISH_SLANG_DICT = {
    "fire": "amazing",
    "slaps": "tastes great", 
    "lit": "exciting",
    "dope": "excellent",
    "sick": "impressive",
    "bruh": "brother",
    "cap": "lie",
    "bet": "agreement",
    "sus": "suspicious",
    "ghost": "ignore",
    "salty": "bitter",
    "clout": "fame",
    "flex": "show off",
    "woke": "aware",
    "tea": "gossip",
    "vibe": "atmosphere",
    "yeet": "throw",
    "simp": "overly attentive",
    "incel": "involuntary celibate",
    "thirsty": "eager for attention",
    # Curated additions
    "sheesh": "impressive",
    "drip": "stylish clothing",
    "bussin": "very tasty",
    "lowkey": "secretly",
    "highkey": "openly",
    "goat": "greatest of all time",
    "mid": "mediocre",
    "movie": "cinematic quality",
    "wildin": "behaving wildly",
    "yikes": "embarrassing",
    "valid": "legitimate",
    "clutch": "critical success",
    "cold": "excellent",
    # Phrases
    "no cap": "no lie",
    "built different": "exceptional",
    "rent free": "occupying mind persistently",
    "touch grass": "go outside",
    "left no crumbs": "outperformed others",
    "say less": "i understand",
    "giving main character": "standing out confidently",
    "keep the same energy": "maintain the same attitude",
    "understood the assignment": "performed exceptionally",
    "vibes": "atmosphere",
    "w": "win",
    "l": "loss",
    "chief": "leader"
}

# Hinglish to English mapping
HINGLISH_DICT = {
    "bhai": "brother",
    "bro": "brother",
    "ye": "this",
    "wo": "that", 
    "kya": "what",
    "kaise": "how",
    "kyu": "why",
    "accha": "good",
    "mast": "excellent",
    "jhakaas": "fantastic",
    "badiya": "good",
    "yaar": "friend",
    "dost": "friend",
    "pagal": "crazy",
    "nashta": "snack",
    "sahi": "correct",
    "ganda": "bad",
    "chutiya": "fool",
    "behen": "sister", 
    "chod": "leave",
    "karo": "do",
    "hai": "is",
    "tha": "was",
    "thi": "was",
    "hain": "are",
    "op": "outstanding",
    "bhayanak": "scary",
    "zabardast": "terrific",
    "kamal": "wonderful",
    # Curated additions
    "bakchodi": "nonsense",
    "majak": "joke",
    "jugaad": "workaround",
    "faadu": "awesome",
    "bawal": "extraordinary",
    "bindaas": "carefree",
    "bhaiya": "brother",
    "behenji": "sister"
}

# Merge in auto-updates if available
_updates = _load_updates()
EMOJI_DICT.update(_updates.get("EMOJI_DICT", {}))
ENGLISH_SLANG_DICT.update(_updates.get("ENGLISH_SLANG_DICT", {}))
HINGLISH_DICT.update(_updates.get("HINGLISH_DICT", {}))

def normalize_text(text, lang='both'):
    """
    Normalize text by replacing slang and emojis
    
    Args:
        text (str): Input text to normalize
        lang (str): 'english', 'hinglish', or 'both'
    """
    if not isinstance(text, str):
        return text
        
    normalized = text
    
    # Replace emojis first, skip placeholders
    for emoji, meaning in EMOJI_DICT.items():
        if isinstance(meaning, str) and meaning.strip().lower().startswith('todo'):
            continue
        normalized = normalized.replace(emoji, f' {meaning} ')
    
    # Replace slang based on language
    if lang in ['english', 'both']:
        for slang, meaning in ENGLISH_SLANG_DICT.items():
            if isinstance(meaning, str) and meaning.strip().lower().startswith('todo'):
                continue
            normalized = re.sub(r'\b' + re.escape(slang) + r'\b', meaning, normalized, flags=re.IGNORECASE)
    
    if lang in ['hinglish', 'both']:
        for slang, meaning in HINGLISH_DICT.items():
            if isinstance(meaning, str) and meaning.strip().lower().startswith('todo'):
                continue
            normalized = re.sub(r'\b' + re.escape(slang) + r'\b', meaning, normalized, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    normalized = ' '.join(normalized.split())
    
    return normalized