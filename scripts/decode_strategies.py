import os
import argparse
from typing import List, Dict
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def load(model_dir: str):
    tok = AutoTokenizer.from_pretrained(model_dir)
    mdl = AutoModelForSeq2SeqLM.from_pretrained(model_dir)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    mdl.to(device)
    return mdl, tok, device

def greedy_decode(texts: List[str], model, tokenizer, device, max_length: int):
    outs = []
    for t in texts:
        ids = tokenizer(t, return_tensors="pt", truncation=True).to(device)
        gen = model.generate(**ids, max_length=max_length)
        outs.append(tokenizer.decode(gen[0], skip_special_tokens=True))
    return outs

def beam_decode(texts: List[str], model, tokenizer, device, max_length: int, num_beams: int, no_repeat_ngram_size: int, length_penalty: float, n_best: int):
    outs = []
    scores = []
    for t in texts:
        ids = tokenizer(t, return_tensors="pt", truncation=True).to(device)
        gen = model.generate(
            **ids,
            max_length=max_length,
            num_beams=num_beams,
            no_repeat_ngram_size=no_repeat_ngram_size,
            length_penalty=length_penalty,
            num_return_sequences=n_best,
            return_dict_in_generate=True,
            output_scores=True,
        )
        seqs = [tokenizer.decode(s, skip_special_tokens=True) for s in gen.sequences]
        outs.append(seqs)
        scores.append(gen.sequences_scores.tolist() if gen.sequences_scores is not None else [])
    return outs, scores

def sampling_decode(texts: List[str], model, tokenizer, device, max_length: int, top_k: int, top_p: float, temperature: float, n_best: int):
    outs = []
    for t in texts:
        ids = tokenizer(t, return_tensors="pt", truncation=True).to(device)
        gen = model.generate(
            **ids,
            max_length=max_length,
            do_sample=True,
            top_k=top_k,
            top_p=top_p,
            temperature=temperature,
            num_return_sequences=n_best,
        )
        seqs = [tokenizer.decode(s, skip_special_tokens=True) for s in gen]
        outs.append(seqs)
    return outs

def compare_strategies(text: str, model_dir: str, max_length: int = 128, num_beams: int = 6, no_repeat_ngram_size: int = 3, length_penalty: float = 1.0, n_best: int = 3, top_k: int = 50, top_p: float = 0.95, temperature: float = 1.0) -> Dict[str, object]:
    mdl, tok, dev = load(model_dir)
    greedy = greedy_decode([text], mdl, tok, dev, max_length)[0]
    beams, scores = beam_decode([text], mdl, tok, dev, max_length, num_beams, no_repeat_ngram_size, length_penalty, n_best)
    samples = sampling_decode([text], mdl, tok, dev, max_length, top_k, top_p, temperature, n_best)
    return {"greedy": greedy, "beam": {"outputs": beams[0], "scores": scores[0]}, "sampling": samples[0]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_dir", type=str, required=True)
    parser.add_argument("--text", type=str, required=True)
    parser.add_argument("--max_length", type=int, default=128)
    parser.add_argument("--num_beams", type=int, default=6)
    parser.add_argument("--no_repeat_ngram_size", type=int, default=3)
    parser.add_argument("--length_penalty", type=float, default=1.0)
    parser.add_argument("--n_best", type=int, default=3)
    parser.add_argument("--top_k", type=int, default=50)
    parser.add_argument("--top_p", type=float, default=0.95)
    parser.add_argument("--temperature", type=float, default=1.0)
    args = parser.parse_args()
    res = compare_strategies(args.text, args.model_dir, args.max_length, args.num_beams, args.no_repeat_ngram_size, args.length_penalty, args.n_best, args.top_k, args.top_p, args.temperature)
    print(res)

if __name__ == "__main__":
    main()