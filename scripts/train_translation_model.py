"""
Trains a T5-based translation model using the Hugging Face Seq2SeqTrainer.

This script fine-tunes a pretrained T5 model on a custom dataset for translating
slang/memes to standard English. It handles loading the tokenized dataset,
configuring training arguments, and running the training and evaluation loop.

Model Used:
  - google/flan-t5-base (or other T5 variants)

Input Format:
  - A tokenized Hugging Face `DatasetDict` from 'outputs/tokenized_dataset'.

Output Format:
  - A fine-tuned model saved to 'outputs/translation_model/'.
  - Training logs and checkpoints in 'outputs/training_results/'.

Dataset Path:
  - Input: 'outputs/tokenized_dataset'
"""
import os
import argparse
import numpy as np
import evaluate
from datasets import load_from_disk
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
)

# Get the absolute path to the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- Configuration ---
MODEL_CHECKPOINT = "google/flan-t5-base"
TOKENIZED_DATASET_PATH = os.path.join(PROJECT_ROOT, "outputs", "tokenized_dataset")
MODEL_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "translation_model")
TRAINING_RESULTS_DIR = os.path.join(PROJECT_ROOT, "outputs", "training_results")

# --- BLEU Metric ---
metric = evaluate.load("sacrebleu")

def postprocess_text(preds, labels):
    preds = [pred.strip() for pred in preds]
    labels = [[label.strip()] for label in labels]
    return preds, labels

def compute_metrics(eval_preds):
    preds, labels = eval_preds
    if isinstance(preds, tuple):
        preds = preds[0]
    
    # Replace -100 (ignore index) with pad token ID
    preds = np.where(preds != -100, preds, tokenizer.pad_token_id)
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)

    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    # Post-processing for BLEU
    decoded_preds, decoded_labels = postprocess_text(decoded_preds, decoded_labels)

    result = metric.compute(predictions=decoded_preds, references=decoded_labels)
    result = {"bleu": result["score"]}

    prediction_lens = [np.count_nonzero(pred != tokenizer.pad_token_id) for pred in preds]
    result["gen_len"] = np.mean(prediction_lens)
    result = {k: round(v, 4) for k, v in result.items()}
    return result

def main():
    """
    Main function to set up and run the training process.
    """
    parser = argparse.ArgumentParser(description="Train a T5 translation model.")
    parser.add_argument("--model_checkpoint", type=str, default=MODEL_CHECKPOINT, help="Model checkpoint for training.")
    parser.add_argument("--epochs", type=int, default=15, help="Number of training epochs.")
    parser.add_argument("--batch_size", type=int, default=16, help="Training and evaluation batch size.")
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate.")
    parser.add_argument("--weight_decay", type=float, default=0.01, help="Weight decay for optimizer")
    parser.add_argument("--use-cpu", action="store_true", help="Force use of CPU even if GPU is available")
    args = parser.parse_args()

    print(f"Starting training with model: {args.model_checkpoint}")

    # --- Load Tokenizer and Model ---
    global tokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.model_checkpoint)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_checkpoint)

    # --- Load Tokenized Dataset ---
    try:
        tokenized_datasets = load_from_disk(TOKENIZED_DATASET_PATH)
        print(f"Loaded tokenized dataset: {tokenized_datasets}")
    except FileNotFoundError:
        print(f"Error: Tokenized dataset not found at {TOKENIZED_DATASET_PATH}.")
        print("Please run `prepare_tokenized_dataset.py` first.")
        return

    # --- Data Collator ---
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    # --- Training Arguments ---
    training_args = Seq2SeqTrainingArguments(
        output_dir=TRAINING_RESULTS_DIR,
        eval_strategy="epoch",
        save_strategy="epoch",
        report_to="none",
        learning_rate=args.lr,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        weight_decay=args.weight_decay,
        num_train_epochs=args.epochs,
        predict_with_generate=True,
        fp16=False,  # Disable mixed-precision if causing issues
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        no_cuda=args.use_cpu,
    )

    # Initialize Trainer
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    # --- Train the Model ---
    print("Starting model training...")
    try:
        trainer.train()
        print("Training complete.")
    except Exception as e:
        print(f"An error occurred during training: {e}")
        return

    # --- Save the Best Model ---
    try:
        trainer.save_model(MODEL_OUTPUT_DIR)
        print(f"Best model saved to {MODEL_OUTPUT_DIR}")
    except Exception as e:
        print(f"Error saving the model: {e}")

if __name__ == "__main__":
    main()