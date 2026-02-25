import os
import sys
import json
import argparse
import pandas as pd
import torch
import evaluate
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Add the parent directory to sys.path so we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.config_loader import load_config

# Constants
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_CONFIG_PATH = os.path.join(ROOT, "config.yaml")
DEFAULT_DATA_PATH = os.path.join(ROOT, "outputs", "datasets", "test.csv")
DEFAULT_MODEL_PATH = os.path.join(ROOT, "outputs", "translation_model")
DEFAULT_OUT_PATH = os.path.join(ROOT, "results", "metrics.json")

def load_model_and_tokenizer(model_path: str):
    """Load the fine-tuned model and tokenizer."""
    print(f"Loading model from {model_path}...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    return model, tokenizer, device

def generate_translations(model, tokenizer, device, inputs, config):
    """Generate translations for a list of input texts."""
    gen_cfg = config["generation"]
    model_cfg = config["model"]
    
    translations = []
    print("Generating translations...")
    for text in tqdm(inputs):
        input_ids = tokenizer(text, return_tensors="pt", truncation=True).input_ids.to(device)
        with torch.no_grad():
            output_ids = model.generate(
                input_ids,
                max_length=model_cfg["max_target_length"],
                num_beams=gen_cfg["num_beams"],
                no_repeat_ngram_size=gen_cfg["no_repeat_ngram_size"],
                length_penalty=gen_cfg["length_penalty"],
                early_stopping=True
            )
        translations.append(tokenizer.decode(output_ids[0], skip_special_tokens=True).strip())
    return translations

def calculate_metrics(predictions, references):
    """Calculate BLEU, SacreBLEU, ChrF, and BERTScore."""
    print("Calculating metrics...")
    
    # Load metrics
    bleu_metric = evaluate.load("bleu")
    sacrebleu_metric = evaluate.load("sacrebleu")
    chrf_metric = evaluate.load("chrf")
    bertscore_metric = evaluate.load("bertscore")
    
    results = {}
    
    # BLEU
    results["bleu"] = bleu_metric.compute(predictions=predictions, references=[[r] for r in references])["bleu"]
    
    # SacreBLEU
    results["sacrebleu"] = sacrebleu_metric.compute(predictions=predictions, references=[[r] for r in references])["score"]
    
    # ChrF
    results["chrf"] = chrf_metric.compute(predictions=predictions, references=[[r] for r in references])["score"]
    
    # BERTScore
    bertscore_res = bertscore_metric.compute(predictions=predictions, references=references, lang="en")
    results["bertscore_precision"] = sum(bertscore_res["precision"]) / len(bertscore_res["precision"])
    results["bertscore_recall"] = sum(bertscore_res["recall"]) / len(bertscore_res["recall"])
    results["bertscore_f1"] = sum(bertscore_res["f1"]) / len(bertscore_res["f1"])
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Evaluation Script for Slang Translator")
    parser.add_argument("--config", type=str, default=DEFAULT_CONFIG_PATH, help="Path to config.yaml")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL_PATH, help="Path to the trained model")
    parser.add_argument("--data", type=str, default=DEFAULT_DATA_PATH, help="Path to the test CSV file")
    parser.add_argument("--output", type=str, default=DEFAULT_OUT_PATH, help="Path to save metrics.json")
    args = parser.parse_args()

    # 1. Load config
    config = load_config(args.config)
    
    # 2. Load model
    model, tokenizer, device = load_model_and_tokenizer(args.model)
    
    # 3. Load test data
    df = pd.read_csv(args.data)
    inputs = df["input_text"].astype(str).tolist()
    references = df["target_text"].astype(str).tolist()
    
    # 4. Generate
    predictions = generate_translations(model, tokenizer, device, inputs, config)
    
    # 5. Calculate metrics
    metrics = calculate_metrics(predictions, references)
    
    # 6. Save results
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)
    
    print(f"\nEvaluation Results saved to {args.output}:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")

if __name__ == "__main__":
    main()
