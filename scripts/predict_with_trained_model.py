"""
Prediction demo for the trained translation model.

Model used: Loads fine-tuned seq2seq from `outputs/translation_model/`.
Input format: Either a `--text` string or reads samples from `outputs/datasets/test.csv`.
Output format: Prints predictions; optionally saves to `outputs/data/predictions.csv`.
Dataset path: `cross-language-meme-slang-translator/outputs/datasets/test.csv`.
Purpose: Provide a quick inference demo for the trained model.

CLI options:
- `--model`: directory of the trained model or checkpoint
- `--text`: single input string to translate
- `--num_beams`: decoding beam size (default 4)
- `--max_new_tokens`: maximum generated tokens (default 128)
- `--save`: save sample predictions CSV
"""

import os
import argparse
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEST_CSV = os.path.join(PROJECT_ROOT, "outputs", "datasets", "test.csv")
MODEL_DIR = os.path.join(PROJECT_ROOT, "outputs", "translation_model")
PRED_OUT = os.path.join(PROJECT_ROOT, "outputs", "data", "predictions.csv")


def predict_text(model, tokenizer, text: str, num_beams: int = 4, max_new_tokens: int = 128) -> str:
    input_ids = tokenizer(
        "translate to english: " + text,
        return_tensors="pt",
        truncation=True,
        max_length=max_new_tokens,
    ).input_ids
    outputs = model.generate(input_ids, max_new_tokens=max_new_tokens, num_beams=num_beams)
    return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()


def main():
    parser = argparse.ArgumentParser(description="Prediction demo for trained model")
    parser.add_argument("--model", type=str, default=MODEL_DIR, help="Model directory")
    parser.add_argument("--text", type=str, default=None, help="Single input text to translate")
    parser.add_argument("--num_beams", type=int, default=4, help="Beam size for generation")
    parser.add_argument("--max_new_tokens", type=int, default=128, help="Max new tokens for generation")
    parser.add_argument("--save", action="store_true", help="Save predictions to outputs/data/predictions.csv")
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model)

    if args.text:
        pred = predict_text(model, tokenizer, args.text, num_beams=args.num_beams, max_new_tokens=args.max_new_tokens)
        print(f"Input: {args.text}\nPrediction: {pred}")
        return

    if not os.path.exists(TEST_CSV):
        raise FileNotFoundError(f"Missing test CSV: {TEST_CSV}. Run split_dataset_70_20_10.py.")
    df = pd.read_csv(TEST_CSV)
    samples = df.head(10).copy()
    samples["prediction"] = samples["input_text"].map(lambda x: predict_text(model, tokenizer, str(x), num_beams=args.num_beams, max_new_tokens=args.max_new_tokens))
    print(samples[["input_text", "target_text", "prediction"]])

    if args.save:
        os.makedirs(os.path.dirname(PRED_OUT), exist_ok=True)
        samples.to_csv(PRED_OUT, index=False)
        print(f"Saved predictions to: {PRED_OUT}")


if __name__ == "__main__":
    main()