import os
import argparse
import pandas as pd
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)
from dataset.slang_emoji_dict import normalize_text

def dedupe(path: str, out_path: str, source_col: str, target_col: str):
    df = pd.read_csv(path) if path.lower().endswith(".csv") else pd.read_excel(path)
    df = df.dropna(subset=[source_col, target_col]).copy()
    df[source_col] = df[source_col].astype(str).map(lambda x: normalize_text(x, lang="both"))
    df[target_col] = df[target_col].astype(str).map(lambda x: normalize_text(x, lang="english"))
    df = df[(df[source_col] != "") & (df[target_col] != "")]
    df = df.drop_duplicates(subset=[source_col, target_col])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if out_path.lower().endswith(".csv"):
        df.to_csv(out_path, index=False)
    else:
        df.to_excel(out_path, index=False)
    return out_path, len(df)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--source_col", type=str, default="Slang/Meme Text")
    parser.add_argument("--target_col", type=str, default="Standard Translation")
    args = parser.parse_args()
    out, n = dedupe(args.input, args.output, args.source_col, args.target_col)
    print({"saved": out, "rows": n})

if __name__ == "__main__":
    main()