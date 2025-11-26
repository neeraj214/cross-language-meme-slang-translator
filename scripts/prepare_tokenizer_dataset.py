"""
Tokenize train/val/test CSVs for seq2seq translation using a chosen tokenizer.

Model used: Default `google/flan-t5-base` (T5-family), configurable via CLI.
Input format: CSVs under `outputs/datasets/` with columns `input_text`, `target_text`.
Output format: Tokenized HuggingFace `DatasetDict` saved to `outputs/tokenized_dataset`.
Dataset path: `cross-language-meme-slang-translator/outputs/datasets/train.csv|val.csv|test.csv`.
Purpose: Build tokenized datasets ready for PyTorch training.
"""

import os
import argparse
from typing import Dict

import pandas as pd
from datasets import Dataset, DatasetDict
from transformers import AutoTokenizer


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "outputs", "datasets")
OUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "tokenized_dataset")


def load_splits() -> Dict[str, Dataset]:
    paths = {
        "train": os.path.join(DATA_DIR, "train.csv"),
        "validation": os.path.join(DATA_DIR, "val.csv"),
        "test": os.path.join(DATA_DIR, "test.csv"),
    }
    for name, path in paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing split file: {path}. Run split_dataset_70_20_10.py first.")
    def to_hf(path):
        df = pd.read_csv(path)
        if "input_text" not in df.columns or "target_text" not in df.columns:
            raise ValueError("CSV must contain 'input_text' and 'target_text' columns")
        return Dataset.from_pandas(df)
    return {k: to_hf(v) for k, v in paths.items()}


def main():
    parser = argparse.ArgumentParser(description="Prepare tokenized dataset for translation")
    parser.add_argument("--model", type=str, default="google/flan-t5-base", help="Tokenizer/model checkpoint")
    parser.add_argument("--source_prefix", type=str, default="translate to english: ", help="Optional prefix to prepend to inputs")
    parser.add_argument("--max_source_length", type=int, default=128, help="Max source length")
    parser.add_argument("--max_target_length", type=int, default=128, help="Max target length")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    splits = load_splits()

    def preprocess(batch):
        inputs = [args.source_prefix + x for x in batch["input_text"]]
        model_inputs = tokenizer(
            inputs,
            max_length=args.max_source_length,
            truncation=True,
        )
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(
                batch["target_text"],
                max_length=args.max_target_length,
                truncation=True,
            )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    tokenized = {}
    for name, ds in splits.items():
        tokenized[name] = ds.map(preprocess, batched=True, remove_columns=ds.column_names)

    ds_dict = DatasetDict(tokenized)
    ds_dict.save_to_disk(OUT_DIR)
    print(f"Saved tokenized DatasetDict to: {OUT_DIR}")


if __name__ == "__main__":
    main()