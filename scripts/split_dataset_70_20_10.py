"""
Split the normalized slang dataset into train/val/test CSVs with cleaning.

Model used: Any seq2seq translator (downstream uses `google/flan-t5-base`).
Input format: Excel file `dataset/processed/normalized_slang_dataset.xlsx` with columns:
  - `Slang/Meme Text` (input)
  - `Standard Translation` (target)
Output format: CSVs saved under `outputs/datasets/` with columns:
  - `input_text`
  - `target_text`
Dataset path: `cross-language-meme-slang-translator/dataset/processed/normalized_slang_dataset.xlsx`
Purpose: Clean data, normalize text, split into 70/20/10 and save train/val/test.
"""

import os
import re
import unicodedata
from typing import Tuple

import pandas as pd


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_XLSX = os.path.join(
    PROJECT_ROOT, "dataset", "processed", "normalized_slang_dataset.xlsx"
)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "datasets")


def _normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    # Unicode NFKC normalization
    text = unicodedata.normalize("NFKC", text)
    # Lowercase
    text = text.lower()
    # Replace multiple whitespace with single space
    text = re.sub(r"\s+", " ", text).strip()
    # Remove zero-width and control characters
    text = "".join(ch for ch in text if ch.isprintable())
    return text


def _load_and_clean(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    if "Slang/Meme Text" not in df.columns or "Standard Translation" not in df.columns:
        raise ValueError(
            "Input Excel must contain 'Slang/Meme Text' and 'Standard Translation' columns"
        )
    df = df[["Slang/Meme Text", "Standard Translation"]].rename(
        columns={"Slang/Meme Text": "input_text", "Standard Translation": "target_text"}
    )
    # Drop NaNs, strip and normalize
    df = df.dropna(subset=["input_text", "target_text"]).copy()
    df["input_text"] = df["input_text"].astype(str).map(_normalize_text)
    df["target_text"] = df["target_text"].astype(str).map(_normalize_text)
    # Drop empty and duplicates
    df = df[(df["input_text"] != "") & (df["target_text"] != "")]
    df = df.drop_duplicates(subset=["input_text", "target_text"])  # prevent leakage via duplicates
    return df.reset_index(drop=True)


def _split_df(df: pd.DataFrame, seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Shuffle deterministically
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    n = len(df)
    n_train = int(0.7 * n)
    n_val = int(0.2 * n)
    train_df = df.iloc[:n_train]
    val_df = df.iloc[n_train : n_train + n_val]
    test_df = df.iloc[n_train + n_val :]
    return train_df, val_df, test_df


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Loading dataset from: {DATASET_XLSX}")
    df = _load_and_clean(DATASET_XLSX)
    print(f"Total cleaned rows: {len(df)}")
    train_df, val_df, test_df = _split_df(df)
    train_path = os.path.join(OUTPUT_DIR, "train.csv")
    val_path = os.path.join(OUTPUT_DIR, "val.csv")
    test_path = os.path.join(OUTPUT_DIR, "test.csv")
    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)
    print("Saved:")
    print(f"  Train: {train_path} ({len(train_df)})")
    print(f"  Val:   {val_path} ({len(val_df)})")
    print(f"  Test:  {test_path} ({len(test_df)})")


if __name__ == "__main__":
    main()