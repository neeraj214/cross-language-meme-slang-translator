#!/usr/bin/env python
import os
import subprocess
import time
import argparse
import json
import pandas as pd
import emoji
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def check_model_ready(checkpoint_dir):
    if not os.path.exists(checkpoint_dir):
        return False
    has_config = os.path.exists(os.path.join(checkpoint_dir, "config.json"))
    has_tokenizer = os.path.exists(os.path.join(checkpoint_dir, "tokenizer.json"))
    has_weights = os.path.exists(os.path.join(checkpoint_dir, "pytorch_model.bin")) or os.path.exists(os.path.join(checkpoint_dir, "model.safetensors"))
    return has_config and has_tokenizer and has_weights

def run_command(command):
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    for line in process.stdout:
        print(line.strip())
    process.wait()
    return process.returncode

def generate_preds(model_dir, texts, max_length=64, num_beams=6, no_repeat_ngram_size=3, length_penalty=1.0):
    tok = AutoTokenizer.from_pretrained(model_dir)
    mdl = AutoModelForSeq2SeqLM.from_pretrained(model_dir)
    outs = []
    for t in texts:
        ids = tok(t, return_tensors="pt", truncation=True)
        gen = mdl.generate(
            ids.input_ids,
            attention_mask=ids.attention_mask,
            max_length=max_length,
            num_beams=num_beams,
            no_repeat_ngram_size=no_repeat_ngram_size,
            length_penalty=length_penalty
        )
        outs.append(tok.decode(gen[0], skip_special_tokens=True).strip())
    return outs

def has_emoji(s):
    return any(ch in emoji.EMOJI_DATA for ch in s)

def has_slang(s):
    slang = {"bhai","yaar","pro","vibe","lit","fire","roast","cringe","bro","lol","iconic","savage","goat","op"}
    tokens = {t.strip(".,!?\"'()").lower() for t in s.split()}
    return any(t in slang for t in tokens)

def lexical_diversity(s):
    toks = [t.strip(".,!?\"'()").lower() for t in s.split() if t.strip()]
    if not toks:
        return 0.0
    return len(set(toks)) / len(toks)

def write_style_metrics(label, sources, preds, out_path):
    e = [1.0 if has_emoji(p) else 0.0 for p in preds]
    s = [1.0 if has_slang(p) else 0.0 for p in preds]
    d = [lexical_diversity(p) for p in preds]
    payload = {
        label: {
            "emoji_presence": sum(e) / len(e) if e else 0.0,
            "slang_presence": sum(s) / len(s) if s else 0.0,
            "lexical_diversity": sum(d) / len(d) if d else 0.0,
            "samples": [{"source": src, "pred": p} for src, p in list(zip(sources, preds))[:10]]
        }
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if os.path.exists(out_path):
        with open(out_path, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
                if not isinstance(existing, dict):
                    existing = {}
            except Exception:
                existing = {}
    else:
        existing = {}
    existing.update(payload)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)
    print({label: existing[label]})

def main():
    parser = argparse.ArgumentParser(description="Run evaluations for trained models")
    parser.add_argument("--forward_model", default="outputs/checkpoints/t5-small-forward-ep5-lr3e4-64")
    parser.add_argument("--reverse_model", default="outputs/checkpoints/t5-small-reverse-ep5-lr3e4-64")
    parser.add_argument("--wait", action="store_true")
    parser.add_argument("--max_wait_time", type=int, default=7200)
    args = parser.parse_args()

    if args.wait:
        start_time = time.time()
        while time.time() - start_time < args.max_wait_time:
            f_ready = check_model_ready(args.forward_model)
            r_ready = check_model_ready(args.reverse_model)
            if f_ready and r_ready:
                break
            time.sleep(60)

    os.makedirs("results/metrics", exist_ok=True)

    if check_model_ready(args.forward_model):
        run_command(
            "python scripts/evaluate_sacrebleu.py "
            f"--model {args.forward_model} "
            f"--csv outputs/datasets/val.csv "
            f"--source_col input_text "
            f"--target_col target_text "
            f"--out results/metrics/sacrebleu_forward.json"
        )
        run_command(
            "python scripts/evaluate_sacrebleu.py "
            f"--model {args.forward_model} "
            f"--csv outputs/datasets/test.csv "
            f"--source_col input_text "
            f"--target_col target_text "
            f"--out results/metrics/sacrebleu_forward.json"
        )
        df_val_f = pd.read_csv("outputs/datasets/val.csv")
        df_test_f = pd.read_csv("outputs/datasets/test.csv")
        f_val_src = df_val_f["input_text"].astype(str).tolist()
        f_test_src = df_test_f["input_text"].astype(str).tolist()
        f_val_preds = generate_preds(args.forward_model, f_val_src)
        f_test_preds = generate_preds(args.forward_model, f_test_src)
        write_style_metrics("forward_val", f_val_src, f_val_preds, "results/metrics/style_metrics.json")
        write_style_metrics("forward_test", f_test_src, f_test_preds, "results/metrics/style_metrics.json")
        rich = os.path.join("outputs", "data", "test.csv")
        if os.path.exists(rich):
            run_command(
                "python scripts/evaluate_sacrebleu.py "
                f"--model {args.forward_model} "
                f"--csv {rich} "
                f"--source_col input_text "
                f"--target_col target_text "
                f"--out results/metrics/sacrebleu_forward_rich_raw.json"
            )
            run_command(
                "python scripts/evaluate_sacrebleu.py "
                f"--model {args.forward_model} "
                f"--csv {rich} "
                f"--source_col Normalized_Text "
                f"--target_col Normalized_Translation "
                f"--out results/metrics/sacrebleu_forward_rich_norm.json"
            )
    else:
        print(f"Forward model not ready at {args.forward_model}")

    if check_model_ready(args.reverse_model):
        run_command(
            "python scripts/evaluate_sacrebleu.py "
            f"--model {args.reverse_model} "
            f"--csv outputs/datasets/reverse_val.csv "
            f"--source_col source_text "
            f"--target_col target_text "
            f"--out results/metrics/sacrebleu_reverse.json"
        )
        run_command(
            "python scripts/evaluate_sacrebleu.py "
            f"--model {args.reverse_model} "
            f"--csv outputs/datasets/reverse_test.csv "
            f"--source_col source_text "
            f"--target_col target_text "
            f"--out results/metrics/sacrebleu_reverse.json"
        )
        df_val = pd.read_csv("outputs/datasets/reverse_val.csv")
        df_test = pd.read_csv("outputs/datasets/reverse_test.csv")
        val_src = df_val["source_text"].astype(str).tolist()
        test_src = df_test["source_text"].astype(str).tolist()
        val_preds = generate_preds(args.reverse_model, val_src)
        test_preds = generate_preds(args.reverse_model, test_src)
        write_style_metrics("reverse_val", val_src, val_preds, "results/metrics/style_metrics.json")
        write_style_metrics("reverse_test", test_src, test_preds, "results/metrics/style_metrics.json")
    else:
        print(f"Reverse model not ready at {args.reverse_model}")

    print("All evaluations completed")

if __name__ == "__main__":
    main()
