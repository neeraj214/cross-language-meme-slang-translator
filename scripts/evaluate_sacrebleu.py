import os
import json
import argparse
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results", "metrics")

def generate(model, tokenizer, texts, num_beams, max_new_tokens, no_repeat_ngram_size, length_penalty):
    outs = []
    for t in texts:
        ids = tokenizer(t, return_tensors="pt", truncation=True)
        gen = model.generate(
            ids.input_ids,
            attention_mask=ids.attention_mask,
            max_new_tokens=max_new_tokens,
            num_beams=num_beams,
            no_repeat_ngram_size=no_repeat_ngram_size,
            length_penalty=length_penalty,
        )
        outs.append(tokenizer.decode(gen[0], skip_special_tokens=True).strip())
    return outs

def corpus_and_sentence_bleu(preds, refs):
    import sacrebleu
    corp = sacrebleu.corpus_bleu(preds, [[r] for r in refs], smooth_method="exp")
    sent = []
    for p, r in zip(preds, refs):
        s = sacrebleu.sentence_bleu(p, [r], smooth_method="exp")
        sent.append(float(s.score))
    return float(corp.score), sent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default=os.path.join(PROJECT_ROOT, "outputs", "translation_model"))
    parser.add_argument("--csv", type=str, default=os.path.join(PROJECT_ROOT, "outputs", "datasets", "test.csv"))
    parser.add_argument("--source_col", type=str, default="input_text")
    parser.add_argument("--target_col", type=str, default="target_text")
    parser.add_argument("--num_beams", type=int, default=6)
    parser.add_argument("--max_new_tokens", type=int, default=128)
    parser.add_argument("--no_repeat_ngram_size", type=int, default=3)
    parser.add_argument("--length_penalty", type=float, default=1.0)
    parser.add_argument("--out", type=str, default=os.path.join(RESULTS_DIR, "sacrebleu.json"))
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    df = pd.read_csv(args.csv)
    inputs = df[args.source_col].astype(str).tolist()
    refs = df[args.target_col].astype(str).tolist()
    tok = AutoTokenizer.from_pretrained(args.model)
    mdl = AutoModelForSeq2SeqLM.from_pretrained(args.model)
    preds = generate(mdl, tok, inputs, args.num_beams, args.max_new_tokens, args.no_repeat_ngram_size, args.length_penalty)
    corp, sent = corpus_and_sentence_bleu(preds, refs)
    payload = {"corpus_bleu": corp, "sentence_bleu": sent[:50], "samples": [{"source": s, "pred": p, "ref": r} for s, p, r in zip(inputs[:10], preds[:10], refs[:10])]}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(payload)

if __name__ == "__main__":
    main()