import re

VARIANTS = {
    "bhai": ["bhai", "bhaii", "bhaiya", "bhay"],
    "yaar": ["yaar", "yarr", "yar", "yaarrr"],
    "mast": ["mast", "must", "mastt"],
    "bakchodi": ["bakchodi", "bakchodiya", "bakchod"],
    "acha": ["acha", "accha", "achha"],
    "pura": ["pura", "poora", "puraah"],
    "scene": ["scene", "seen", "scn"],
    "level": ["level", "lvl", "lewl"],
    "dialogue": ["dialogue", "dialog", "dilog"],
    "viral": ["viral", "wyral", "vyral"],
    "trend": ["trend", "trand", "treand"],
    "relatable": ["relatable", "reltbl", "relatble"],
    "meme": ["meme", "meem", "mem"],
    "friend": ["friend", "frnd", "fren"],
    "roast": ["roast", "rost", "roassst"],
    "vibe": ["vibe", "vaib", "vayybe"],
    "bakwaas": ["bakwaas", "bakwas", "bakvaas"],
    "sahi": ["sahi", "sahi", "sai"],
    "pagal": ["pagal", "paagal", "pagl"],
}

def normalize_hinglish(text: str) -> str:
    if not isinstance(text, str):
        return text
    s = text.lower()
    for base, vars in VARIANTS.items():
        for v in vars:
            s = re.sub(r"\b" + re.escape(v) + r"\b", base, s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

