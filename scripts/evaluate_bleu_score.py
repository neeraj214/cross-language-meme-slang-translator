"""
Evaluate BLEU scores (Forward, Reverse, Average) on the test set with smoothing.

Model used: Loads fine-tuned seq2seq from `outputs/translation_model/` or a checkpoint via --model.
Input format: CSV test split `outputs/datasets/test.csv` with columns `input_text`, `target_text`.
Output format: Prints BLEU scores and saves to `results/metrics/bleu_scores.json`.
Dataset path: `cross-language-meme-slang-translator/outputs/datasets/test.csv`.
Purpose: Quantify translation performance with sacreBLEU smoothing and report metrics.

CLI options:
- `--model`: directory of the trained model or checkpoint
- `--num_beams`: decoding beam size (default 4)
- `--max_new_tokens`: maximum generated tokens (default 128)
"""

import os
import json
import argparse

import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEST_CSV = os.path.join(PROJECT_ROOT, "outputs", "datasets", "test.csv")
MODEL_DIR = os.path.join(PROJECT_ROOT, "outputs", "translation_model")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results", "metrics")


def compute_bleu_scores(preds, refs):
    try:
        import sacrebleu
        forward = sacrebleu.corpus_bleu(preds, [[r] for r in refs], smooth_method="exp").score
        reverse = sacrebleu.corpus_bleu(refs, [[p] for p in preds], smooth_method="exp").score
    except Exception:
        # Fallback: naive average using nltk
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
        smoothie = SmoothingFunction().method4
        forward = sum(sentence_bleu([r.split()], p.split(), smoothing_function=smoothie) for p, r in zip(preds, refs)) * 100.0 / max(len(preds), 1)
        reverse = sum(sentence_bleu([p.split()], r.split(), smoothing_function=smoothie) for p, r in zip(preds, refs)) * 100.0 / max(len(refs), 1)
    average = (forward + reverse) / 2.0
    return round(forward, 4), round(reverse, 4), round(average, 4)


def compute_exact_match(preds, refs):
    """Compute strict exact-match accuracy (case-sensitive) between predictions and references."""
    if not preds:
        return 0.0
    exact = sum(int(p.strip() == r.strip()) for p, r in zip(preds, refs)) / float(len(preds))
    return round(exact * 100.0, 2)  # percentage


def generate_predictions(model, tokenizer, inputs, num_beams: int = 4, max_new_tokens: int = 128):
    preds = []
    for text in inputs:
        input_ids = tokenizer(
            "translate to english: " + text,
            return_tensors="pt",
            truncation=True,
            max_length=max_new_tokens,
        ).input_ids
        outputs = model.generate(input_ids, max_new_tokens=max_new_tokens, num_beams=num_beams)
        pred = tokenizer.decode(outputs[0], skip_special_tokens=True)
        preds.append(pred.strip())
    return preds


def main():
    parser = argparse.ArgumentParser(description="Evaluate BLEU scores on test set")
    parser.add_argument("--model", type=str, default=MODEL_DIR, help="Model directory")
    parser.add_argument("--num_beams", type=int, default=4, help="Beam size for generation")
    parser.add_argument("--max_new_tokens", type=int, default=128, help="Max new tokens for generation")
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    if not os.path.exists(TEST_CSV):
        raise FileNotFoundError(f"Missing test CSV: {TEST_CSV}. Run split_dataset_70_20_10.py.")

    df = pd.read_csv(TEST_CSV)
    inputs = df["input_text"].astype(str).tolist()
    refs = df["target_text"].astype(str).tolist()

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model)

    preds = generate_predictions(model, tokenizer, inputs, num_beams=args.num_beams, max_new_tokens=args.max_new_tokens)
    fwd, rev, avg = compute_bleu_scores(preds, refs)
    em_pct = compute_exact_match(preds, refs)

    print({"Forward BLEU": fwd, "Reverse BLEU": rev, "Average BLEU": avg, "Exact Match %": em_pct})
    out_path = os.path.join(RESULTS_DIR, "bleu_scores.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"forward": fwd, "reverse": rev, "average": avg, "exact_match_percent": em_pct}, f, indent=2)
    print(f"Saved BLEU metrics to: {out_path}")


if __name__ == "__main__":
    main()