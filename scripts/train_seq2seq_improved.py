import os
import argparse
import numpy as np
from datasets import load_from_disk
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, DataCollatorForSeq2Seq, Seq2SeqTrainer, Seq2SeqTrainingArguments, EarlyStoppingCallback

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOKENIZED_DIR = os.path.join(PROJECT_ROOT, "outputs", "tokenized_dataset")
MODEL_OUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "translation_model")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "outputs", "training_results")

def compute_metrics_builder(tokenizer):
    try:
        import sacrebleu
        use_sacrebleu = True
    except Exception:
        import evaluate
        bleu_metric = evaluate.load("sacrebleu")
        use_sacrebleu = False
    def compute_metrics(eval_preds):
        preds, labels = eval_preds
        if isinstance(preds, tuple):
            preds = preds[0]
        preds = np.where(preds != -100, preds, tokenizer.pad_token_id)
        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
        decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
        decoded_preds = [p.strip() for p in decoded_preds]
        decoded_labels = [[l.strip()] for l in decoded_labels]
        if use_sacrebleu:
            bleu = sacrebleu.corpus_bleu(decoded_preds, decoded_labels, smooth_method="exp")
            bleu_score = float(bleu.score)
        else:
            res = bleu_metric.compute(predictions=decoded_preds, references=decoded_labels)
            bleu_score = float(res["score"]) if isinstance(res, dict) else float(res)
        exact = float(np.mean([int(p == r[0]) for p, r in zip(decoded_preds, decoded_labels)]))
        gen_lens = [np.count_nonzero(np.array(pred) != tokenizer.pad_token_id) for pred in preds]
        return {"bleu": round(bleu_score, 4), "exact_match": round(exact, 4), "gen_len": float(np.mean(gen_lens))}
    return compute_metrics

class FreezeCallback(EarlyStoppingCallback):
    def __init__(self, freeze_encoder_epochs=0, early_stopping_patience=3, early_stopping_threshold=0.0):
        super().__init__(early_stopping_patience=early_stopping_patience, early_stopping_threshold=early_stopping_threshold)
        self.freeze_encoder_epochs = freeze_encoder_epochs
    def on_epoch_begin(self, args, state, control, **kwargs):
        model = kwargs.get("model")
        if model is None:
            return control
        freeze = state.epoch < self.freeze_encoder_epochs
        for n, p in model.named_parameters():
            if "encoder" in n:
                p.requires_grad = not freeze
        return control

class CustomTrainer(Seq2SeqTrainer):
    def __init__(self, encoder_lr_mult=1.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoder_lr_mult = encoder_lr_mult
    def create_optimizer(self):
        if self.optimizer is not None:
            return
        import torch
        from torch.optim import AdamW
        no_decay = ["bias", "LayerNorm.weight"]
        encoder_params = []
        decoder_params = []
        for n, p in self.model.named_parameters():
            if not p.requires_grad:
                continue
            if "encoder" in n:
                encoder_params.append((n, p))
            else:
                decoder_params.append((n, p))
        def group(params, lr):
            wd = []
            nwd = []
            for n, p in params:
                if any(nd in n for nd in no_decay):
                    nwd.append(p)
                else:
                    wd.append(p)
            return [
                {"params": wd, "weight_decay": self.args.weight_decay, "lr": lr},
                {"params": nwd, "weight_decay": 0.0, "lr": lr},
            ]
        base_lr = self.args.learning_rate
        groups = []
        groups.extend(group(encoder_params, base_lr * self.encoder_lr_mult))
        groups.extend(group(decoder_params, base_lr))
        self.optimizer = AdamW(groups, betas=(0.9, 0.999), eps=1e-8)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="google/flan-t5-base")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--warmup_steps", type=int, default=1000)
    parser.add_argument("--weight_decay", type=float, default=0.01)
    parser.add_argument("--fp16", action="store_true")
    parser.add_argument("--label_smoothing", type=float, default=0.1)
    parser.add_argument("--encoder_lr_mult", type=float, default=0.5)
    parser.add_argument("--freeze_encoder_epochs", type=int, default=0)
    parser.add_argument("--source_prefix", type=str, default="translate to english: ")
    parser.add_argument("--gen_max_length", type=int, default=128)
    parser.add_argument("--gen_num_beams", type=int, default=6)
    parser.add_argument("--gen_no_repeat_ngram", type=int, default=3)
    parser.add_argument("--gen_length_penalty", type=float, default=1.0)
    parser.add_argument("--tokenized_dir", type=str, default=TOKENIZED_DIR)
    parser.add_argument("--model_out_dir", type=str, default=MODEL_OUT_DIR)
    parser.add_argument("--results_dir", type=str, default=RESULTS_DIR)
    args = parser.parse_args()

    os.makedirs(args.model_out_dir, exist_ok=True)
    os.makedirs(args.results_dir, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model)

    try:
        tokenized = load_from_disk(args.tokenized_dir)
    except FileNotFoundError:
        raise FileNotFoundError(f"Tokenized dataset not found: {args.tokenized_dir}")

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    training_args = Seq2SeqTrainingArguments(
        output_dir=args.results_dir,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=args.lr,
        warmup_steps=args.warmup_steps,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        weight_decay=args.weight_decay,
        num_train_epochs=args.epochs,
        predict_with_generate=True,
        fp16=args.fp16,
        load_best_model_at_end=True,
        metric_for_best_model="bleu",
        greater_is_better=True,
        save_total_limit=3,
        logging_strategy="steps",
        logging_steps=50,
        generation_max_length=args.gen_max_length,
        generation_num_beams=args.gen_num_beams,
        generation_no_repeat_ngram_size=args.gen_no_repeat_ngram,
        generation_length_penalty=args.gen_length_penalty,
        label_smoothing_factor=args.label_smoothing,
    )

    trainer = CustomTrainer(
        encoder_lr_mult=args.encoder_lr_mult,
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics_builder(tokenizer),
        callbacks=[FreezeCallback(args.freeze_encoder_epochs, early_stopping_patience=3)],
    )

    trainer.train()
    trainer.save_model(args.model_out_dir)

if __name__ == "__main__":
    main()