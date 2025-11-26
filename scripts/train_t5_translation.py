"""
Train a T5-family translation model using Hugging Face Seq2SeqTrainer.

Model used: Default `google/flan-t5-base` (preferred), configurable via CLI.
Input format: Tokenized `DatasetDict` from `outputs/tokenized_dataset`.
Output format: Fine-tuned model saved to `outputs/translation_model/` and logs/checkpoints to `outputs/training_results/`.
Dataset path: `cross-language-meme-slang-translator/outputs/tokenized_dataset`.
Purpose: Full training with validation, logging loss/accuracy/BLEU, save best model.
"""

import os
import argparse
import numpy as np
from typing import Tuple

from datasets import load_from_disk
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOKENIZED_DIR = os.path.join(PROJECT_ROOT, "outputs", "tokenized_dataset")
MODEL_OUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "translation_model")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "outputs", "training_results")


def postprocess_text(preds, labels):
    preds = [p.strip() for p in preds]
    labels = [[l.strip()] for l in labels]
    return preds, labels


def compute_metrics_builder(tokenizer):
    try:
        import sacrebleu
        use_sacrebleu = True
    except Exception:
        import evaluate
        bleu_metric = evaluate.load("sacrebleu")
        use_sacrebleu = False

    def compute_metrics(eval_preds: Tuple[np.ndarray, np.ndarray]):
        preds, labels = eval_preds
        if isinstance(preds, tuple):
            preds = preds[0]
        # Replace -100 with pad id for decoding
        preds = np.where(preds != -100, preds, tokenizer.pad_token_id)
        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)

        decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
        decoded_preds, decoded_labels = postprocess_text(decoded_preds, decoded_labels)

        # BLEU with smoothing
        if use_sacrebleu:
            bleu = sacrebleu.corpus_bleu(decoded_preds, decoded_labels, smooth_method="exp")
            bleu_score = float(bleu.score)
        else:
            res = bleu_metric.compute(predictions=decoded_preds, references=decoded_labels)
            bleu_score = float(res["score"]) if isinstance(res, dict) else float(res)

        # Exact match accuracy
        exact = float(np.mean([int(p == r[0]) for p, r in zip(decoded_preds, decoded_labels)]))

        # Generation length
        gen_lens = [np.count_nonzero(np.array(pred) != tokenizer.pad_token_id) for pred in preds]
        return {"bleu": round(bleu_score, 4), "exact_match": round(exact, 4), "gen_len": float(np.mean(gen_lens))}

    return compute_metrics


def main():
    parser = argparse.ArgumentParser(description="Train T5 translation model")
    parser.add_argument("--model", type=str, default="google/flan-t5-base", help="Model checkpoint")
    parser.add_argument("--epochs", type=int, default=15, help="Training epochs (10–20 recommended)")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size (8 or 16)")
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate")
    parser.add_argument("--warmup_steps", type=int, default=500, help="Warmup steps")
    parser.add_argument("--weight_decay", type=float, default=0.01, help="Weight decay")
    parser.add_argument("--use-cpu", action="store_true", help="Use CPU even if GPU is available")
    args = parser.parse_args()

    os.makedirs(MODEL_OUT_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model)

    try:
        tokenized = load_from_disk(TOKENIZED_DIR)
    except FileNotFoundError:
        raise FileNotFoundError(f"Tokenized dataset not found: {TOKENIZED_DIR}. Run prepare_tokenizer_dataset.py first.")

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    training_args = Seq2SeqTrainingArguments(
        output_dir=RESULTS_DIR,
        eval_strategy="epoch",
        save_strategy="epoch",
        report_to="none",  # disable wandb
        learning_rate=args.lr,
        warmup_steps=args.warmup_steps,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        weight_decay=args.weight_decay,
        num_train_epochs=args.epochs,
        predict_with_generate=True,
        fp16=False,
        load_best_model_at_end=True,
        metric_for_best_model="bleu",
        greater_is_better=True,
        no_cuda=args.use_cpu,
        save_total_limit=3,
        logging_strategy="steps",
        logging_steps=50,
        generation_max_length=128,
        generation_num_beams=4,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics_builder(tokenizer),
    )

    print("Starting training...")
    trainer.train()
    print("Training finished. Saving best model...")
    trainer.save_model(MODEL_OUT_DIR)
    print(f"Model saved to: {MODEL_OUT_DIR}")


if __name__ == "__main__":
    main()