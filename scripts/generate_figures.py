import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
METRICS_DIR = os.path.join(BASE_DIR, "results", "metrics")
FIG_DIR = os.path.join(BASE_DIR, "results", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def bleu_bar(forward_path, reverse_path):
    f = load_json(forward_path)
    r = load_json(reverse_path)
    fwd = float(f["corpus_bleu"])
    rev = float(r["corpus_bleu"])
    avg = (fwd + rev) / 2.0
    scores = [fwd, rev, avg]
    labels = ["Forward", "Reverse", "Average"]
    plt.figure(figsize=(6, 4))
    sns.barplot(x=labels, y=scores, palette=["#4c78a8", "#f58518", "#54a24b"])
    plt.ylabel("Corpus BLEU")
    plt.title("BLEU Scores")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "bleu_bar.png"), dpi=200)
    plt.close()

def token_dist(forward_csv):
    df = pd.read_csv(forward_csv)
    a = df["input_text"].astype(str).map(lambda x: len(x.split()))
    b = df["target_text"].astype(str).map(lambda x: len(x.split()))
    plt.figure(figsize=(7, 4))
    sns.histplot(a, bins=30, color="#4c78a8", alpha=0.6, label="Input")
    sns.histplot(b, bins=30, color="#f58518", alpha=0.6, label="Target")
    plt.legend()
    plt.xlabel("Word Count")
    plt.title("Token-Length Distribution")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "token_lengths.png"), dpi=200)
    plt.close()

def error_types(forward_path):
    f = load_json(forward_path)
    cats = {"copy": 0, "code_mix_retained": 0, "brevity": 0, "emoji_generic": 0, "other": 0}
    for s in f.get("samples", []):
        src = s.get("source", "").strip().lower()
        pred = s.get("pred", "").strip().lower()
        ref = s.get("ref", "").strip().lower()
        if pred == src or pred == ref:
            cats["copy"] += 1
        elif any(w in pred for w in ["bhai", "yaar", "accha", "acha", "kyu", "kyun", "hain"]):
            cats["code_mix_retained"] += 1
        elif len(pred.split()) <= 3:
            cats["brevity"] += 1
        elif any(w in pred for w in ["laughing hard", "amazing", "cool", "love"]):
            cats["emoji_generic"] += 1
        else:
            cats["other"] += 1
    labels = list(cats.keys())
    values = [cats[k] for k in labels]
    plt.figure(figsize=(7, 4))
    sns.barplot(x=labels, y=values, palette="pastel")
    plt.ylabel("Count")
    plt.title("Error-Type Distribution (Heuristic)")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "error_types.png"), dpi=200)
    plt.close()

def sample_grid(forward_path, reverse_path):
    f = load_json(forward_path).get("samples", [])
    r = load_json(reverse_path).get("samples", [])
    samples = []
    for s in f[:3]:
        samples.append(("Forward", s.get("source", ""), s.get("pred", ""), s.get("ref", "")))
    for s in r[:3]:
        samples.append(("Reverse", s.get("source", ""), s.get("pred", ""), s.get("ref", "")))
    plt.figure(figsize=(10, 6))
    plt.axis("off")
    y = 0.95
    for i, (d, src, pred, ref) in enumerate(samples):
        txt = f"{d}\nInput: {src}\nOutput: {pred}\nRef: {ref}\n"
        plt.text(0.02, y, txt, fontsize=9, va="top")
        y -= 0.15
    plt.title("Sample Outputs")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "samples.png"), dpi=200)
    plt.close()

def main():
    fwd_json = os.path.join(METRICS_DIR, "sacrebleu_forward.json")
    rev_json = os.path.join(METRICS_DIR, "sacrebleu_reverse.json")
    fwd_csv = os.path.join(BASE_DIR, "outputs", "datasets", "test.csv")
    bleu_bar(fwd_json, rev_json)
    token_dist(fwd_csv)
    error_types(fwd_json)
    sample_grid(fwd_json, rev_json)
    print({"figures": ["bleu_bar.png", "token_lengths.png", "error_types.png", "samples.png"], "dir": FIG_DIR})

if __name__ == "__main__":
    main()
