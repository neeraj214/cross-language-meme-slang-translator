import os
import argparse
import json
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import sacrebleu

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEF_DATA_DIR = os.path.join(ROOT, "outputs", "datasets_v2")

def _load_csvs(data_dir: str):
    test = pd.read_csv(os.path.join(data_dir, "test.csv"))
    return test

def _collect_refs(row):
    refs = [str(row["target_text"]).strip()]
    for k in row.index:
        if k.startswith("target_ref_"):
            v = str(row[k]).strip()
            if v:
                refs.append(v)
    return refs

def _generate(model, tok, device, inputs, max_new_tokens, num_beams, no_repeat_ngram_size, length_penalty, repetition_penalty):
    outs = []
    for s in inputs:
        enc = tok(s, return_tensors="pt", truncation=True).to(device)
        g = model.generate(
            **enc,
            max_new_tokens=max_new_tokens,
            num_beams=num_beams,
            no_repeat_ngram_size=no_repeat_ngram_size,
            length_penalty=length_penalty,
            repetition_penalty=repetition_penalty,
        )
        outs.append(tok.decode(g[0], skip_special_tokens=True))
    return outs

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model_dir", type=str, required=True)
    p.add_argument("--direction", type=str, choices=["forward", "reverse"], default="forward")
    p.add_argument("--data_dir", type=str, default=DEF_DATA_DIR)
    p.add_argument("--max_new_tokens", type=int, default=128)
    p.add_argument("--num_beams", type=int, default=6)
    p.add_argument("--no_repeat_ngram", type=int, default=3)
    p.add_argument("--length_penalty", type=float, default=1.0)
    p.add_argument("--repetition_penalty", type=float, default=1.2)
    p.add_argument("--out_path", type=str, default=os.path.join(ROOT, "results", "metrics", "bleu_updated.json"))
    args = p.parse_args()

    test = _load_csvs(args.data_dir)
    tok = AutoTokenizer.from_pretrained(args.model_dir)
    mdl = AutoModelForSeq2SeqLM.from_pretrained(args.model_dir)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    mdl.to(device)

    if args.direction == "forward":
        inputs = ["translate to english: " + s for s in test["input_text"].astype(str).tolist()]
        refs_multi = [ _collect_refs(r) for _, r in test.iterrows() ]
        preds = _generate(mdl, tok, device, inputs, args.max_new_tokens, args.num_beams, args.no_repeat_ngram, args.length_penalty, args.repetition_penalty)
        bleu = sacrebleu.corpus_bleu(preds, refs_multi)
        out = {"direction": "forward", "bleu_score": float(bleu.score), "sys_len": int(bleu.sys_len), "ref_len": int(bleu.ref_len), "bp": float(bleu.bp)}
    else:
        inputs = ["translate to slang: " + s for s in test["target_text"].astype(str).tolist()]
        refs_multi = [ [str(r["input_text"]).strip()] for _, r in test.iterrows() ]
        preds = _generate(mdl, tok, device, inputs, args.max_new_tokens, args.num_beams, args.no_repeat_ngram, args.length_penalty, args.repetition_penalty)
        bleu = sacrebleu.corpus_bleu(preds, refs_multi)
        out = {"direction": "reverse", "bleu_score": float(bleu.score), "sys_len": int(bleu.sys_len), "ref_len": int(bleu.ref_len), "bp": float(bleu.bp)}

    os.makedirs(os.path.dirname(args.out_path), exist_ok=True)
    with open(args.out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()

