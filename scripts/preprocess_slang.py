import os
import argparse
import pandas as pd
from dataset.slang_emoji_dict import normalize_text
from scripts.hinglish_normalization import normalize_hinglish

DEF_INPUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset", "processed", "normalized_slang_dataset.csv")
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "datasets_v2")

def _load(path: str) -> pd.DataFrame:
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    return pd.read_excel(path)

def _normalize_row(src: str, tgt: str, lang: str) -> tuple:
    src2 = normalize_hinglish(src) if lang.lower() == "hinglish" else src
    src2 = normalize_text(src2, lang="both")
    tgt2 = normalize_text(tgt, lang="english")
    return src2, tgt2

def _aggregate_multi_refs(df: pd.DataFrame, src_col: str, tgt_col: str, lang_col: str) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        src, tgt = _normalize_row(str(r[src_col]), str(r[tgt_col]), str(r[lang_col]))
        rows.append({"input_text": src, "target_text": tgt, "lang": r[lang_col]})
    d2 = pd.DataFrame(rows)
    d2 = d2.dropna(subset=["input_text", "target_text"]).copy()
    d2 = d2[(d2["input_text"] != "") & (d2["target_text"] != "")]
    grouped = d2.groupby(["input_text", "lang"])['target_text'].apply(list).reset_index(name='targets')
    out_rows = []
    for _, r in grouped.iterrows():
        base = {"input_text": r["input_text"], "lang": r["lang"]}
        tlist = list(dict.fromkeys(r["targets"]))
        base["target_text"] = tlist[0]
        for i, t in enumerate(tlist[1:], start=1):
            base[f"target_ref_{i}"] = t
        out_rows.append(base)
    return pd.DataFrame(out_rows)

def _split(df: pd.DataFrame, train_ratio=0.7, val_ratio=0.2):
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    n = len(df)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    train = df.iloc[:n_train]
    val = df.iloc[n_train:n_train+n_val]
    test = df.iloc[n_train+n_val:]
    return train, val, test

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=str, default=DEF_INPUT)
    p.add_argument("--source_col", type=str, default="Slang/Meme Text")
    p.add_argument("--target_col", type=str, default="Standard Translation")
    p.add_argument("--lang_col", type=str, default="Language")
    p.add_argument("--out_dir", type=str, default=OUT_DIR)
    args = p.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    df = _load(args.input)
    df = df.dropna(subset=[args.source_col, args.target_col, args.lang_col]).copy()
    proc = _aggregate_multi_refs(df, args.source_col, args.target_col, args.lang_col)
    tr, va, te = _split(proc)
    tr.to_csv(os.path.join(args.out_dir, "train.csv"), index=False)
    va.to_csv(os.path.join(args.out_dir, "val.csv"), index=False)
    te.to_csv(os.path.join(args.out_dir, "test.csv"), index=False)

if __name__ == "__main__":
    main()

