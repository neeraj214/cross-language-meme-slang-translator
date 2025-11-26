#!/usr/bin/env python
"""
Run all evaluations for both forward and reverse models.
This script automates the evaluation process by running BLEU score evaluations
and style metrics evaluations on both validation and test sets.
"""

import os
import subprocess
import time
import argparse

def check_model_ready(checkpoint_dir):
    """Check if model checkpoint directory contains saved model files."""
    if not os.path.exists(checkpoint_dir):
        return False
    
    # Check for essential model files
    required_files = ["config.json", "pytorch_model.bin", "tokenizer.json"]
    for file in required_files:
        if not os.path.exists(os.path.join(checkpoint_dir, file)):
            return False
    
    return True

def run_command(command):
    """Run a command and print its output."""
    print(f"Running: {command}")
    process = subprocess.Popen(
        command, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Print output in real-time
    for line in process.stdout:
        print(line.strip())
    
    process.wait()
    return process.returncode

def main():
    parser = argparse.ArgumentParser(description="Run all evaluations for trained models")
    parser.add_argument("--forward_model", default="outputs/checkpoints/t5-small-forward-ep5-lr3e4-64", 
                        help="Path to forward model checkpoint directory")
    parser.add_argument("--reverse_model", default="outputs/checkpoints/t5-small-reverse-ep5-lr3e4-64", 
                        help="Path to reverse model checkpoint directory")
    parser.add_argument("--wait", action="store_true", 
                        help="Wait for models to be ready before evaluating")
    parser.add_argument("--max_wait_time", type=int, default=7200,
                        help="Maximum wait time in seconds (default: 2 hours)")
    args = parser.parse_args()
    
    # Wait for models if requested
    if args.wait:
        print(f"Waiting for models to be ready (max {args.max_wait_time} seconds)...")
        start_time = time.time()
        forward_ready = False
        reverse_ready = False
        
        while time.time() - start_time < args.max_wait_time:
            if not forward_ready:
                forward_ready = check_model_ready(args.forward_model)
                if forward_ready:
                    print(f"Forward model ready at {args.forward_model}")
            
            if not reverse_ready:
                reverse_ready = check_model_ready(args.reverse_model)
                if reverse_ready:
                    print(f"Reverse model ready at {args.reverse_model}")
            
            if forward_ready and reverse_ready:
                print("Both models are ready. Starting evaluations...")
                break
            
            # Wait 60 seconds before checking again
            print("Waiting for models to be ready...")
            time.sleep(60)
        
        if not (forward_ready and reverse_ready):
            print("Maximum wait time exceeded. Proceeding with available models.")
    
    # Create results directory if it doesn't exist
    os.makedirs("results/metrics", exist_ok=True)
    
    # Forward model BLEU evaluations
    if check_model_ready(args.forward_model):
        print("\n=== Running Forward Model BLEU Evaluations ===")
        
        # Validation set
        run_command(
            f"python scripts/evaluate_bleu_score.py "
            f"--val_csv dataset/processed/val.csv "
            f"--model_dir {args.forward_model} "
            f"--max_length 64 "
            f"--output_file results/metrics/forward_bleu.json "
            f"--label forward_val"
        )
        
        # Test set
        run_command(
            f"python scripts/evaluate_bleu_score.py "
            f"--val_csv dataset/processed/test.csv "
            f"--model_dir {args.forward_model} "
            f"--max_length 64 "
            f"--output_file results/metrics/forward_bleu.json "
            f"--label forward_test"
        )
    else:
        print(f"Forward model not ready at {args.forward_model}. Skipping forward evaluations.")
    
    # Reverse model BLEU evaluations
    if check_model_ready(args.reverse_model):
        print("\n=== Running Reverse Model BLEU Evaluations ===")
        
        # Validation set
        run_command(
            f"python scripts/evaluate_bleu_score.py "
            f"--val_csv outputs/datasets/reverse_val.csv "
            f"--model_dir {args.reverse_model} "
            f"--max_length 64 "
            f"--output_file results/metrics/reverse_bleu.json "
            f"--label reverse_val"
        )
        
        # Test set
        run_command(
            f"python scripts/evaluate_bleu_score.py "
            f"--val_csv outputs/datasets/reverse_test.csv "
            f"--model_dir {args.reverse_model} "
            f"--max_length 64 "
            f"--output_file results/metrics/reverse_bleu.json "
            f"--label reverse_test"
        )
        
        # Style metrics for reverse model
        print("\n=== Running Reverse Model Style Metrics ===")
        
        # Validation set
        run_command(
            f"python scripts/evaluate_style_metrics.py "
            f"--val_csv outputs/datasets/reverse_val.csv "
            f"--model_dir {args.reverse_model} "
            f"--max_length 64 "
            f"--output_file results/metrics/style_metrics.json "
            f"--label reverse_val"
        )
        
        # Test set
        run_command(
            f"python scripts/evaluate_style_metrics.py "
            f"--val_csv outputs/datasets/reverse_test.csv "
            f"--model_dir {args.reverse_model} "
            f"--max_length 64 "
            f"--output_file results/metrics/style_metrics.json "
            f"--label reverse_test"
        )
    else:
        print(f"Reverse model not ready at {args.reverse_model}. Skipping reverse evaluations.")
    
    print("\nAll evaluations completed!")

if __name__ == "__main__":
    main()