#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to extract Hinglish data from the cleaned_slang_translations.csv file
and prepare it for training the T5 model.
"""

import pandas as  pd
import os
import re
import argparse
from sklearn.model_selection import train_test_split

def is_hinglish(text):
    """Check if text contains Hinglish patterns."""
    # Common Hinglish patterns
    hinglish_patterns = [
        r'\b(kya|kyun|kaise|acha|theek|hai|hota|nahi|matlab|lekin|par|aur|mein|ko|se|ki|ka|ke|na|ho|karo|karenge|karna|karoge)\b',
        r'\b(yaar|bhai|dost|didi|behen|beta|beti|ji|haan|naa|accha|thoda|bahut|jyada|kam|bilkul|ekdum)\b',
        r'\b(chal|jaa|aa|dekh|sun|bol|samajh|kar|le|de|rakh|nikal|mil|laga|bana|khaa|pee|so|uth|baith)\b'
    ]
    
    # Check if any Hinglish pattern is in the text
    for pattern in hinglish_patterns:
        if re.search(pattern, text.lower()):
            return True
    
    return False

def extract_hinglish_data(csv_path, output_dir):
    """Extract Hinglish data from CSV and split into train/val/test sets."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Filter rows containing Hinglish text
    hinglish_rows = []
    for _, row in df.iterrows():
        slang = str(row['Slang/Meme Text'])
        standard = str(row['Standard Translation'])
        
        # Check if either slang or standard contains Hinglish
        if is_hinglish(slang) or is_hinglish(standard):
            hinglish_rows.append(row)
    
    # Create a new DataFrame with Hinglish data
    hinglish_df = pd.DataFrame(hinglish_rows)
    
    # Save the full Hinglish dataset
    hinglish_df.to_csv(os.path.join(output_dir, 'hinglish_data.csv'), index=False)
    print(f"Extracted {len(hinglish_df)} Hinglish entries")
    
    # Split into train (70%), validation (15%), and test (15%) sets
    train_df, temp_df = train_test_split(hinglish_df, test_size=0.3, random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)
    
    # Save the splits
    train_df.to_csv(os.path.join(output_dir, 'hinglish_train.csv'), index=False)
    val_df.to_csv(os.path.join(output_dir, 'hinglish_val.csv'), index=False)
    test_df.to_csv(os.path.join(output_dir, 'hinglish_test.csv'), index=False)
    
    # Create forward (slang → standard) datasets in CSV format
    train_df[['Slang/Meme Text', 'Standard Translation']].rename(
        columns={'Slang/Meme Text': 'source_text', 'Standard Translation': 'target_text'}
    ).to_csv(os.path.join(output_dir, 'hinglish_forward_train.csv'), index=False)
    
    val_df[['Slang/Meme Text', 'Standard Translation']].rename(
        columns={'Slang/Meme Text': 'source_text', 'Standard Translation': 'target_text'}
    ).to_csv(os.path.join(output_dir, 'hinglish_forward_val.csv'), index=False)
    
    test_df[['Slang/Meme Text', 'Standard Translation']].rename(
        columns={'Slang/Meme Text': 'source_text', 'Standard Translation': 'target_text'}
    ).to_csv(os.path.join(output_dir, 'hinglish_forward_test.csv'), index=False)
    
    # Create reverse (standard → slang) datasets in CSV format
    train_df[['Standard Translation', 'Slang/Meme Text']].rename(
        columns={'Standard Translation': 'source_text', 'Slang/Meme Text': 'target_text'}
    ).to_csv(os.path.join(output_dir, 'hinglish_reverse_train.csv'), index=False)
    
    val_df[['Standard Translation', 'Slang/Meme Text']].rename(
        columns={'Standard Translation': 'source_text', 'Slang/Meme Text': 'target_text'}
    ).to_csv(os.path.join(output_dir, 'hinglish_reverse_val.csv'), index=False)
    
    test_df[['Standard Translation', 'Slang/Meme Text']].rename(
        columns={'Standard Translation': 'source_text', 'Slang/Meme Text': 'target_text'}
    ).to_csv(os.path.join(output_dir, 'hinglish_reverse_test.csv'), index=False)
    
    print(f"Created train/val/test splits with {len(train_df)}/{len(val_df)}/{len(test_df)} examples")
    print(f"All files saved to {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Extract Hinglish data from CSV')
    parser.add_argument('--csv_path', type=str, default='C:/Users/neera/OneDrive/Documents/NLP_Project/cleaned_slang_translations.csv',
                        help='Path to the cleaned_slang_translations.csv file')
    parser.add_argument('--output_dir', type=str, default='data/hinglish',
                        help='Directory to save the extracted Hinglish data')
    
    args = parser.parse_args()
    extract_hinglish_data(args.csv_path, args.output_dir)

if __name__ == '__main__':
    main()