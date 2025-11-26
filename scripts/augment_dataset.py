import os
import argparse
import random
import pandas as pd

random.seed(42)

def typo_noise(s: str):
    if len(s) < 5:
        return s
    i = random.randint(0, len(s) - 2)
    ops = [lambda x: x[:i] + x[i+1:], lambda x: x[:i] + s[i] + x[i:], lambda x: x[:i] + random.choice("aeiou") + x[i+1:]]
    return ops[random.randint(0, 2)](s)

def hinglish_variants(s: str):
    repl = {"accha": "acha", "kyu": "kyun", "bahut": "bahut", "yaar": "yar", "bhai": "bro"}
    out = s
    for k, v in repl.items():
        out = out.replace(k, v)
    return out

def augment_row(src: str, tgt: str, n: int):
    outs = []
    for _ in range(n):
        a_src = random.choice([src, typo_noise(src), hinglish_variants(src)])
        a_tgt = random.choice([tgt, typo_noise(tgt)])
        outs.append((a_src, a_tgt))
    return outs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--source_col", type=str, default="source_text")
    parser.add_argument("--target_col", type=str, default="target_text")
    parser.add_argument("--num_aug", type=int, default=2)
    parser.add_argument("--out", type=str, required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    rows = []
    for _, r in df.iterrows():
        src = str(r[args.source_col])
        tgt = str(r[args.target_col])
        rows.append((src, tgt))
        rows.extend(augment_row(src, tgt, args.num_aug))
    out_df = pd.DataFrame(rows, columns=["source_text", "target_text"])
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    out_df.to_csv(args.out, index=False)
    print({"saved": args.out, "rows": len(out_df)})

if __name__ == "__main__":
    main()