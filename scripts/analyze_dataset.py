import pandas as pd
import os

def analyze_dataset():
    # Use raw string with 'r' prefix
    dataset_path = r"C:\Users\neera\OneDrive\Documents\NLP_Project\cleaned_slang_translations.xlsx"
    
    try:
        df = pd.read_excel(dataset_path)
        print("=== DATASET ANALYSIS ===")
        print(f"Total samples: {len(df)}")
        print(f"Columns: {df.columns.tolist()}")
        print("\nFirst 5 rows:")
        print(df.head())
        
        if 'Language' in df.columns:
            print(f"\nLanguage distribution:")
            print(df['Language'].value_counts())
            
        # Check for missing values
        print(f"\nMissing values:")
        print(df.isnull().sum())
        
    except FileNotFoundError:
        print(f"Dataset not found at {dataset_path}")
        print("Please update the path in analyze_dataset.py")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    analyze_dataset()