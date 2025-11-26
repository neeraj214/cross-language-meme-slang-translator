import os
import argparse
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_MODEL = os.path.join(PROJECT_ROOT, "outputs", "checkpoints", "t5-small-reverse-ep5-lr3e4-64")
OUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "datasets")

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--csv", type=str, required=True)
    parser.add_argument("--source_col", type=str, default="Standard Translation")
    parser.add_argument("--num_beams", type=int, default=6)
    parser.add_argument("--max_new_tokens", type=int, default=64)
    parser.add_argument("--no_repeat_ngram_size", type=int, default=3)
    parser.add_argument("--length_penalty", type=float, default=1.0)
    parser.add_argument("--out", type=str, default=os.path.join(OUT_DIR, "backtranslated_slang.csv"))
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    df = pd.read_csv(args.csv)
    inputs = df[args.source_col].astype(str).tolist()
    tok = AutoTokenizer.from_pretrained(args.model)
    mdl = AutoModelForSeq2SeqLM.from_pretrained(args.model)
    preds = generate(mdl, tok, inputs, args.num_beams, args.max_new_tokens, args.no_repeat_ngram_size, args.length_penalty)
    out_df = pd.DataFrame({"source_text": df[args.source_col].astype(str), "target_text": preds})
    out_df.to_csv(args.out, index=False)
    print({"saved": args.out, "rows": len(out_df)})

if __name__ == "__main__":
    main()