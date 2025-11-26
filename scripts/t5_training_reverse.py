import os
import argparse
import numpy as np
import evaluate
import pandas as pd
from datasets import Dataset, DatasetDict
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, DataCollatorForSeq2Seq, Seq2SeqTrainer, Seq2SeqTrainingArguments, EarlyStoppingCallback

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEF_DATA_DIR = os.path.join(ROOT, "outputs", "datasets_v2")
MODEL_OUT_DIR = os.path.join(ROOT, "outputs", "translation_model_reverse")
RESULTS_DIR = os.path.join(ROOT, "outputs", "training_results_reverse")

metric = evaluate.load("sacrebleu")

def _load_csvs(data_dir: str) -> DatasetDict:
    train = pd.read_csv(os.path.join(data_dir, "train.csv"))
    val = pd.read_csv(os.path.join(data_dir, "val.csv"))
    test = pd.read_csv(os.path.join(data_dir, "test.csv"))
    return DatasetDict({
        "train": Dataset.from_pandas(train),
        "validation": Dataset.from_pandas(val),
        "test": Dataset.from_pandas(test),
    })

def _tokenize(ds: DatasetDict, tok: AutoTokenizer, source_prefix: str, max_src: int, max_tgt: int) -> DatasetDict:
    def _proc(ex):
        src = [source_prefix + s for s in ex["target_text"]]
        model_inputs = tok(src, max_length=max_src, padding=False, truncation=True)
        labels = tok(ex["input_text"], max_length=max_tgt, padding=False, truncation=True)
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs
    return ds.map(_proc, batched=True, remove_columns=ds["train"].column_names)

def _compute_metrics_builder(tok):
    def _compute(eval_preds):
        preds, labels = eval_preds
        preds = np.where(preds != -100, preds, tok.pad_token_id)
        decoded_preds = tok.batch_decode(preds, skip_special_tokens=True)
        labels = np.where(labels != -100, labels, tok.pad_token_id)
        decoded_labels = tok.batch_decode(labels, skip_special_tokens=True)
        return {"bleu": metric.compute(predictions=decoded_preds, references=[[l] for l in decoded_labels])["score"]}
    return _compute

def _select_easy(ds: Dataset, max_len: int) -> Dataset:
    f = ds.filter(lambda x: len(str(x["target_text"])) <= max_len)
    return f

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=str, default="google/flan-t5-base")
    p.add_argument("--data_dir", type=str, default=DEF_DATA_DIR)
    p.add_argument("--epochs", type=int, default=8)
    p.add_argument("--batch_size", type=int, default=16)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--warmup_steps", type=int, default=1000)
    p.add_argument("--weight_decay", type=float, default=0.01)
    p.add_argument("--source_prefix", type=str, default="translate to slang: ")
    p.add_argument("--max_source_length", type=int, default=128)
    p.add_argument("--max_target_length", type=int, default=128)
    p.add_argument("--beams", type=int, default=6)
    p.add_argument("--no_repeat_ngram_size", type=int, default=3)
    p.add_argument("--length_penalty", type=float, default=1.0)
    p.add_argument("--use_fp16", action="store_true")
    args = p.parse_args()

    os.makedirs(MODEL_OUT_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    ds = _load_csvs(args.data_dir)
    tok = AutoTokenizer.from_pretrained(args.model)
    mdl = AutoModelForSeq2SeqLM.from_pretrained(args.model)
    tok_ds = _tokenize(ds, tok, args.source_prefix, args.max_source_length, args.max_target_length)

    easy_train = _select_easy(ds["train"], 64)
    easy_tok = _tokenize(DatasetDict({"train": easy_train, "validation": ds["validation"]}), tok, args.source_prefix, args.max_source_length, args.max_target_length)

    collator = DataCollatorForSeq2Seq(tok, model=mdl)

    args1 = Seq2SeqTrainingArguments(
        output_dir=RESULTS_DIR,
        learning_rate=args.lr,
        warmup_steps=args.warmup_steps,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        weight_decay=args.weight_decay,
        num_train_epochs=3,
        predict_with_generate=True,
        fp16=args.use_fp16,
        load_best_model_at_end=True,
        metric_for_best_model="bleu",
        greater_is_better=True,
        save_total_limit=3,
        logging_strategy="steps",
        logging_steps=50,
        generation_max_length=args.max_target_length,
        generation_num_beams=args.beams,
        generation_no_repeat_ngram_size=args.no_repeat_ngram,
        generation_length_penalty=args.length_penalty,
    )

    tr1 = Seq2SeqTrainer(
        model=mdl,
        args=args1,
        train_dataset=easy_tok["train"],
        eval_dataset=easy_tok["validation"],
        tokenizer=tok,
        data_collator=collator,
        compute_metrics=_compute_metrics_builder(tok),
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
    )
    tr1.train()

    args2 = Seq2SeqTrainingArguments(
        output_dir=RESULTS_DIR,
        learning_rate=args.lr,
        warmup_steps=args.warmup_steps,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        weight_decay=args.weight_decay,
        num_train_epochs=args.epochs,
        predict_with_generate=True,
        fp16=args.use_fp16,
        load_best_model_at_end=True,
        metric_for_best_model="bleu",
        greater_is_better=True,
        save_total_limit=3,
        logging_strategy="steps",
        logging_steps=50,
        generation_max_length=args.max_target_length,
        generation_num_beams=args.beams,
        generation_no_repeat_ngram_size=args.no_repeat_ngram,
        generation_length_penalty=args.length_penalty,
    )
    tr2 = Seq2SeqTrainer(
        model=mdl,
        args=args2,
        train_dataset=tok_ds["train"],
        eval_dataset=tok_ds["validation"],
        tokenizer=tok,
        data_collator=collator,
        compute_metrics=_compute_metrics_builder(tok),
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
    )
    tr2.train()
    tr2.save_model(MODEL_OUT_DIR)

if __name__ == "__main__":
    main()

