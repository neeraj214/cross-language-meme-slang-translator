import os
import sys
import yaml
import argparse
import numpy as np
import evaluate
import pandas as pd
from datasets import Dataset, DatasetDict
from transformers import (
    AutoTokenizer, 
    AutoModelForSeq2SeqLM, 
    DataCollatorForSeq2Seq, 
    Seq2SeqTrainer, 
    Seq2SeqTrainingArguments, 
    EarlyStoppingCallback
)

# Add the parent directory to sys.path so we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.config_loader import load_config

# Constants
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_CONFIG_PATH = os.path.join(ROOT, "config.yaml")
DEFAULT_DATA_DIR = os.path.join(ROOT, "outputs", "datasets_v2")
DEFAULT_OUT_DIR = os.path.join(ROOT, "models", "final_model")
DEFAULT_LOG_DIR = os.path.join(ROOT, "results", "training_logs")

# Metric
metric = evaluate.load("sacrebleu")

def load_data(data_dir: str) -> DatasetDict:
    """Load train, val, and test datasets from CSV files."""
    try:
        train = pd.read_csv(os.path.join(data_dir, "train.csv"))
        val = pd.read_csv(os.path.join(data_dir, "val.csv"))
        test = pd.read_csv(os.path.join(data_dir, "test.csv"))
        return DatasetDict({
            "train": Dataset.from_pandas(train),
            "validation": Dataset.from_pandas(val),
            "test": Dataset.from_pandas(test),
        })
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

def get_model_and_tokenizer(model_name: str):
    """Load the pre-trained model and tokenizer."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return model, tokenizer

def preprocess_data(ds: DatasetDict, tokenizer, config: dict) -> DatasetDict:
    """Tokenize the dataset based on configuration."""
    max_src = config["model"]["max_source_length"]
    max_tgt = config["model"]["max_target_length"]
    
    def _tokenize_fn(examples):
        model_inputs = tokenizer(
            examples["input_text"], 
            max_length=max_src, 
            padding="max_length", 
            truncation=True
        )
        labels = tokenizer(
            text_target=examples["target_text"], 
            max_length=max_tgt, 
            padding="max_length", 
            truncation=True
        )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    return ds.map(_tokenize_fn, batched=True, remove_columns=ds["train"].column_names)

def compute_metrics_fn(tokenizer):
    """Builder for the compute_metrics function used by the Trainer."""
    def compute_metrics(eval_preds):
        preds, labels = eval_preds
        if isinstance(preds, tuple):
            preds = preds[0]
        
        decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
        
        # Replace -100 in the labels as we can't decode them
        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
        
        # SacreBLEU expects a list of lists for references
        result = metric.compute(predictions=decoded_preds, references=[[l] for l in decoded_labels])
        return {"bleu": result["score"]}
    
    return compute_metrics

def train(model, tokenizer, tokenized_ds, config: dict, output_dir: str, log_dir: str):
    """Initialize and run the Seq2SeqTrainer."""
    training_cfg = config["training"]
    generation_cfg = config["generation"]
    
    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        learning_rate=float(training_cfg["learning_rate"]),
        per_device_train_batch_size=training_cfg["batch_size"],
        per_device_eval_batch_size=training_cfg["batch_size"],
        weight_decay=training_cfg["weight_decay"],
        save_total_limit=3,
        num_train_epochs=training_cfg["epochs"],
        predict_with_generate=True,
        fp16=training_cfg["fp16"],
        logging_dir=log_dir,
        logging_steps=50,
        warmup_ratio=training_cfg["warmup_ratio"],
        gradient_accumulation_steps=training_cfg["gradient_accumulation_steps"],
        seed=training_cfg["seed"],
        label_smoothing_factor=training_cfg["label_smoothing"],
        load_best_model_at_end=True,
        metric_for_best_model="bleu",
        greater_is_better=True,
        generation_max_length=config["model"]["max_target_length"],
        generation_num_beams=generation_cfg["num_beams"],
    )

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
    
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_ds["train"],
        eval_dataset=tokenized_ds["validation"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics_fn(tokenizer),
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
    )

    print("Starting training...")
    trainer.train()
    
    print(f"Saving final model to {output_dir}")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

def main():
    parser = argparse.ArgumentParser(description="Modular T5 Training Pipeline")
    parser.add_argument("--config", type=str, default=DEFAULT_CONFIG_PATH, help="Path to config.yaml")
    parser.add_argument("--data_dir", type=str, default=DEFAULT_DATA_DIR, help="Directory containing train.csv, val.csv, test.csv")
    parser.add_argument("--output_dir", type=str, default=DEFAULT_OUT_DIR, help="Directory to save the trained model")
    parser.add_argument("--log_dir", type=str, default=DEFAULT_LOG_DIR, help="Directory for training logs")
    args = parser.parse_args()

    # 1. Load configuration
    config = load_config(args.config)
    
    # 2. Get model and tokenizer
    model, tokenizer = get_model_and_tokenizer(config["model"]["name"])
    
    # 3. Load data
    dataset = load_data(args.data_dir)
    
    # 4. Preprocess data
    tokenized_ds = preprocess_data(dataset, tokenizer, config)
    
    # 5. Start training
    train(model, tokenizer, tokenized_ds, config, args.output_dir, args.log_dir)

if __name__ == "__main__":
    main()
