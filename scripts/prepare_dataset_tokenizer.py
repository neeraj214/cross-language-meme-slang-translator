"""
Prepare Dataset & Tokenizer Inputs

Model: N/A (Preprocessing utility)
Task: Prepare dataset for meme/slang → English translation
Input: Normalized slang text (from dataset/processed/normalized_slang_dataset.xlsx)
Output: train/val CSVs under outputs/datasets/

Project Context:
This utility prepares bilingual pairs for the Cross-Language Meme & Slang Translator.
It builds source→target pairs using normalized slang text as input and clean English
translation as target, splits into train/val sets, and saves to disk.
"""

import os
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split


def default_paths():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    normalized_default = os.path.join(
        base_dir, "dataset", "processed", "normalized_slang_dataset.xlsx"
    )
    out_dir = os.path.join(base_dir, "outputs", "datasets")
    return normalized_default, out_dir


def load_normalized_dataset(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at {path}")
    if path.lower().endswith(('.xlsx', '.xls')):
        return pd.read_excel(path)
    elif path.lower().endswith('.csv'):
        return pd.read_csv(path)
    # default to excel
    return pd.read_excel(path)


def build_pairs(df: pd.DataFrame, source_col: str, target_col: str) -> pd.DataFrame:
    missing_cols = [c for c in [source_col, target_col] if c not in df.columns]
    if missing_cols:
        raise KeyError(f"Missing required columns: {missing_cols}")

    pairs = df[[source_col, target_col]].rename(
        columns={source_col: "source_text", target_col: "target_text"}
    )

    # Drop rows with empty values
    pairs = pairs.dropna(subset=["source_text", "target_text"]).copy()
    # Basic cleanup
    pairs["source_text"] = pairs["source_text"].astype(str).str.strip()
    pairs["target_text"] = pairs["target_text"].astype(str).str.strip()
    pairs = pairs[(pairs["source_text"] != "") & (pairs["target_text"] != "")]
    return pairs


def split_and_save(pairs: pd.DataFrame, out_dir: str, test_size: float = 0.1, seed: int = 42):
    os.makedirs(out_dir, exist_ok=True)
    train_df, val_df = train_test_split(pairs, test_size=test_size, random_state=seed)
    train_path = os.path.join(out_dir, "train.csv")
    val_path = os.path.join(out_dir, "val.csv")
    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    return train_path, val_path


def main():
    normalized_default, out_dir_default = default_paths()

    parser = argparse.ArgumentParser(description="Prepare train/val datasets for translation")
    parser.add_argument(
        "--dataset_path",
        type=str,
        default=normalized_default,
        help="Path to normalized dataset (.xlsx or .csv)",
    )
    parser.add_argument(
        "--source_col",
        type=str,
        default="Normalized_Text",
        help="Column name for input text",
    )
    parser.add_argument(
        "--target_col",
        type=str,
        default="Standard Translation",
        help="Column name for target text",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default=out_dir_default,
        help="Directory to save train/val CSVs",
    )
    parser.add_argument("--test_size", type=float, default=0.1, help="Validation split size")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()

    df = load_normalized_dataset(args.dataset_path)
    pairs = build_pairs(df, args.source_col, args.target_col)
    train_path, val_path = split_and_save(pairs, args.out_dir, args.test_size, args.seed)

    print("✅ Prepared datasets")
    print("Train:", train_path)
    print("Val:", val_path)
    print("Samples:", len(pairs))


if __name__ == "__main__":
    main()