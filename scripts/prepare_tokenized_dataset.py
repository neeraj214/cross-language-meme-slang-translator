"""
Prepares a tokenized dataset for the translation model.

This script loads the training, validation, and test sets, and then tokenizes
the input and target texts using the specified pretrained model's tokenizer.
The tokenized datasets are saved in a format compatible with PyTorch and the
Hugging Face Trainer.

Model Used:
  - google/flan-t5-base

Input Format:
  - CSV files (train.csv, val.csv, test.csv) with columns 'input_text' and 'target_text'.

Output Format:
  - A Hugging Face `DatasetDict` containing the tokenized and processed
    training, validation, and test sets. Saved to 'outputs/tokenized_dataset'.

Dataset Path:
  - Input: 'outputs/data/train.csv', 'outputs/data/val.csv', 'outputs/data/test.csv'
  - Output: 'outputs/tokenized_dataset'
"""
import os
import argparse
from datasets import load_dataset, DatasetDict
from transformers import AutoTokenizer

# --- Configuration ---
MODEL_CHECKPOINT = "google/flan-t5-base"
MAX_INPUT_LENGTH = 128
MAX_TARGET_LENGTH = 128
OUTPUT_DIR = "outputs/tokenized_dataset"

def main():
    """
    Main function to load, tokenize, and save the dataset.
    """
    parser = argparse.ArgumentParser(description="Tokenize the dataset for translation.")
    parser.add_argument("--model_checkpoint", type=str, default=MODEL_CHECKPOINT, help="Model checkpoint for the tokenizer.")
    parser.add_argument("--output_dir", type=str, default=OUTPUT_DIR, help="Directory to save the tokenized dataset.")
    args = parser.parse_args()

    print(f"Using model checkpoint: {args.model_checkpoint}")

    # --- Load Tokenizer ---
    try:
        tokenizer = AutoTokenizer.from_pretrained(args.model_checkpoint)
        print("Tokenizer loaded successfully.")
    except Exception as e:
        print(f"Error loading tokenizer: {e}")
        return

    # --- Load Datasets ---
    try:
        data_files = {
            "train": "outputs/data/train.csv",
            "validation": "outputs/data/val.csv",
            "test": "outputs/data/test.csv"
        }
        raw_datasets = load_dataset("csv", data_files=data_files)
        print(f"Successfully loaded datasets: {raw_datasets}")
    except FileNotFoundError as e:
        print(f"Error: Dataset file not found. {e}")
        print("Please ensure you have run the `split_dataset_70_20_10.py` script first.")
        return

    # --- Tokenization Function ---
    def preprocess_function(examples):
        inputs = [ex for ex in examples["input_text"]]
        targets = [ex for ex in examples["target_text"]]

        # Tokenize inputs
        model_inputs = tokenizer(
            inputs, max_length=MAX_INPUT_LENGTH, truncation=True, padding="max_length"
        )

        # Tokenize targets
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(
                targets, max_length=MAX_TARGET_LENGTH, truncation=True, padding="max_length"
            )

        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    # --- Apply Tokenization ---
    try:
        tokenized_datasets = raw_datasets.map(
            preprocess_function,
            batched=True,
            remove_columns=raw_datasets["train"].column_names,
        )
        print("Tokenization complete.")
    except Exception as e:
        print(f"Error during tokenization: {e}")
        return

    # --- Save Tokenized Dataset ---
    try:
        tokenized_datasets.save_to_disk(args.output_dir)
        print(f"Tokenized dataset saved to {args.output_dir}")
    except Exception as e:
        print(f"Error saving tokenized dataset: {e}")

if __name__ == "__main__":
    main()