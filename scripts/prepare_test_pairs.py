"""
Prepare Test Source→Target Pairs

Task: Convert the stratified test split into model-ready pairs
Purpose: Build `source_text`/`target_text` for evaluation
Input: `dataset/processed/test.csv` (normalized dataset split)
Output: `outputs/datasets/test.csv` (pairs, filtered, no split)
"""

import os
import argparse
import pandas as pd


def default_paths():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_csv = os.path.join(base_dir, "dataset", "processed", "test.csv")
    out_dir = os.path.join(base_dir, "outputs", "datasets")
    out_path = os.path.join(out_dir, "test.csv")
    return test_csv, out_dir, out_path


def load_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Test CSV not found: {path}")
    return pd.read_csv(path)


def build_pairs(df: pd.DataFrame, source_col: str, target_col: str) -> pd.DataFrame:
    missing = [c for c in [source_col, target_col] if c not in df.columns]
    if missing:
        raise KeyError(f"CSV missing columns: {missing}")

    pairs = df[[source_col, target_col]].rename(
        columns={source_col: "source_text", target_col: "target_text"}
    )

    # Drop rows with empty/NaN
    pairs = pairs.dropna(subset=["source_text", "target_text"]).copy()
    pairs["source_text"] = pairs["source_text"].astype(str).str.strip()
    pairs["target_text"] = pairs["target_text"].astype(str).str.strip()
    pairs = pairs[(pairs["source_text"] != "") & (pairs["target_text"] != "")]

    # Filter out placeholder content
    placeholder = "TODO: add meaning"
    mask = (~pairs["source_text"].str.contains(placeholder)) & (~pairs["target_text"].str.contains(placeholder))
    pairs = pairs[mask].reset_index(drop=True)
    return pairs


def save_pairs(pairs: pd.DataFrame, out_dir: str, out_path: str):
    os.makedirs(out_dir, exist_ok=True)
    pairs.to_csv(out_path, index=False)
    return out_path


def main():
    test_csv_default, out_dir_default, out_path_default = default_paths()

    parser = argparse.ArgumentParser(description="Prepare test pairs without splitting")
    parser.add_argument("--test_csv", type=str, default=test_csv_default, help="Path to stratified test CSV")
    parser.add_argument("--source_col", type=str, default="Normalized_Text", help="Column name for input text")
    parser.add_argument("--target_col", type=str, default="Standard Translation", help="Column name for target text")
    parser.add_argument("--out_dir", type=str, default=out_dir_default, help="Directory to save test pairs")
    parser.add_argument("--out_path", type=str, default=out_path_default, help="Full path for test pairs CSV")
    args = parser.parse_args()

    df = load_csv(args.test_csv)
    pairs = build_pairs(df, args.source_col, args.target_col)
    out_path = save_pairs(pairs, args.out_dir, args.out_path)

    print("✅ Test pairs prepared")
    print("Test pairs:", out_path)
    print("Samples:", len(pairs))


if __name__ == "__main__":
    main()