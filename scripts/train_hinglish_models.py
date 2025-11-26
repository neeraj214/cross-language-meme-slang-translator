#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to train Hinglish T5 models for slang/meme translation.
"""

import os
import argparse
import subprocess

def train_hinglish_models(data_dir, output_dir, epochs=5, batch_size=16, eval_batch_size=8, 
                          learning_rate=3e-4, max_source_length=128, max_target_length=64):
    """Train both forward and reverse Hinglish T5 models."""
    # Create output directories
    forward_output_dir = os.path.join(output_dir, "t5-small-hinglish-forward-ep5-lr3e4-64")
    reverse_output_dir = os.path.join(output_dir, "t5-small-hinglish-reverse-ep5-lr3e4-64")
    
    os.makedirs(forward_output_dir, exist_ok=True)
    os.makedirs(reverse_output_dir, exist_ok=True)
    
    # Train forward model (Hinglish slang → Standard English)
    print("Training Hinglish forward model (Hinglish slang → Standard English)...")
    forward_cmd = [
        "python", "scripts/train_t5_translation.py",
        "--train_csv", os.path.join(data_dir, "hinglish_forward_train.txt"),
        "--val_csv", os.path.join(data_dir, "hinglish_forward_val.txt"),
        "--model_name", "t5-small",
        "--output_dir", forward_output_dir,
        "--metrics_dir", "results/metrics",
        "--epochs", str(epochs),
        "--train_batch_size", str(batch_size),
        "--eval_batch_size", str(eval_batch_size),
        "--lr", str(learning_rate),
        "--max_source_len", str(max_source_length),
        "--max_target_len", str(max_target_length)
    ]
    
    # Train reverse model (Standard English → Hinglish slang)
    print("Training Hinglish reverse model (Standard English → Hinglish slang)...")
    reverse_cmd = [
        "python", "scripts/train_t5_translation.py",
        "--train_csv", os.path.join(data_dir, "hinglish_reverse_train.txt"),
        "--val_csv", os.path.join(data_dir, "hinglish_reverse_val.txt"),
        "--model_name", "t5-small",
        "--output_dir", reverse_output_dir,
        "--metrics_dir", "results/metrics",
        "--epochs", str(epochs),
        "--train_batch_size", str(batch_size),
        "--eval_batch_size", str(eval_batch_size),
        "--lr", str(learning_rate),
        "--max_source_len", str(max_source_length),
        "--max_target_len", str(max_target_length)
    ]
    
    # Return commands for execution
    return forward_cmd, reverse_cmd

def main():
    parser = argparse.ArgumentParser(description='Train Hinglish T5 models')
    parser.add_argument('--data_dir', type=str, default='data/hinglish',
                        help='Directory containing Hinglish datasets')
    parser.add_argument('--output_dir', type=str, default='outputs/checkpoints',
                        help='Directory to save model checkpoints')
    parser.add_argument('--epochs', type=int, default=5,
                        help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=16,
                        help='Training batch size')
    parser.add_argument('--eval_batch_size', type=int, default=8,
                        help='Evaluation batch size')
    parser.add_argument('--learning_rate', type=float, default=3e-4,
                        help='Learning rate')
    parser.add_argument('--max_source_length', type=int, default=128,
                        help='Maximum source sequence length')
    parser.add_argument('--max_target_length', type=int, default=64,
                        help='Maximum target sequence length')
    parser.add_argument('--run', type=str, choices=['forward', 'reverse', 'both'], default='both',
                        help='Which model to train (forward, reverse, or both)')
    
    args = parser.parse_args()
    
    forward_cmd, reverse_cmd = train_hinglish_models(
        args.data_dir, 
        args.output_dir,
        args.epochs,
        args.batch_size,
        args.eval_batch_size,
        args.learning_rate,
        args.max_source_length,
        args.max_target_length
    )
    
    # Train forward model (Hinglish slang → Standard English)
    if args.run in ['forward', 'both']:
        print("Starting Hinglish forward model training...")
        forward_cmd = f"python scripts/train_t5_translation.py --train_csv {os.path.join(args.data_dir, 'hinglish_forward_train.csv')} --val_csv {os.path.join(args.data_dir, 'hinglish_forward_val.csv')} --model_name t5-small --output_dir {os.path.join(args.output_dir, f't5-small-hinglish-forward-ep{args.epochs}-lr{args.learning_rate}-{args.max_target_length}')} --metrics_dir results/metrics --epochs {args.epochs} --train_batch_size {args.batch_size} --eval_batch_size {args.eval_batch_size} --lr {args.learning_rate} --max_source_len {args.max_source_length} --max_target_len {args.max_target_length}"
        print(forward_cmd)
        os.system(forward_cmd)

    # Train reverse model (Standard English → Hinglish slang)
    if args.run in ['reverse', 'both']:
        print("Starting Hinglish reverse model training...")
        reverse_cmd = f"python scripts/train_t5_translation.py --train_csv {os.path.join(args.data_dir, 'hinglish_reverse_train.csv')} --val_csv {os.path.join(args.data_dir, 'hinglish_reverse_val.csv')} --model_name t5-small --output_dir {os.path.join(args.output_dir, f't5-small-hinglish-reverse-ep{args.epochs}-lr{args.learning_rate}-{args.max_target_length}')} --metrics_dir results/metrics --epochs {args.epochs} --train_batch_size {args.batch_size} --eval_batch_size {args.eval_batch_size} --lr {args.learning_rate} --max_source_len {args.max_source_length} --max_target_len {args.max_target_length}"
        print(reverse_cmd)
        os.system(reverse_cmd)

if __name__ == '__main__':
    main()