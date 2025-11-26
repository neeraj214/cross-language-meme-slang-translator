import os
import json
import torch
from transformers import T5ForConditionalGeneration, T5TokenizerFast

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FWD_DIR = os.path.join(BASE_DIR, "outputs", "checkpoints", "t5-small-hinglish-forward-ep5-lr0.0003-64")
REV_DIR = os.path.join(BASE_DIR, "outputs", "checkpoints", "t5-small-hinglish-reverse-ep5-lr0.0003-64")
METRICS_DIR = os.path.join(BASE_DIR, "results", "metrics")

def load(model_dir):
    tok = T5TokenizerFast.from_pretrained(model_dir)
    mdl = T5ForConditionalGeneration.from_pretrained(model_dir)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    mdl.to(device)
    return mdl, tok, device

def generate(text, model, tokenizer, device, max_source_len=128, max_target_len=64):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_source_len).to(device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=max_target_len,
            num_beams=4,
            early_stopping=True,
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def main():
    os.makedirs(METRICS_DIR, exist_ok=True)

    # Samples
    hinglish_sample = "ye post full bakchodi hai, mast laga"
    english_sample = "This post is complete nonsense, loved it"

    # Forward: Hinglish -> English
    fwd_model, fwd_tok, device = load(FWD_DIR)
    fwd_out = generate(hinglish_sample, fwd_model, fwd_tok, device)

    # Reverse: English -> Hinglish
    rev_model, rev_tok, device2 = load(REV_DIR)
    rev_out = generate(english_sample, rev_model, rev_tok, device2)

    payload = {
        "samples": {
            "forward": {
                "input": hinglish_sample,
                "output": fwd_out,
            },
            "reverse": {
                "input": english_sample,
                "output": rev_out,
            },
        }
    }

    out_path = os.path.join(METRICS_DIR, "hinglish_sanity_checks.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print("Saved sanity checks to:", out_path)
    print("Forward sample:")
    print("  Input:", hinglish_sample)
    print("  Output:", fwd_out)
    print("Reverse sample:")
    print("  Input:", english_sample)
    print("  Output:", rev_out)

if __name__ == "__main__":
    main()