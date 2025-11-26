import pandas as pd
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataset.slang_emoji_dict import normalize_text

def normalize_dataset():
    """Normalize the raw dataset using slang and emoji dictionaries"""

    # Paths
    raw_data_path = r"C:\Users\neera\OneDrive\Documents\NLP_Project\cleaned_slang_translations.xlsx"
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dataset", "processed", "normalized_slang_dataset.xlsx")
    
    try:
        # Read raw data
        print("Reading raw dataset...")
        if raw_data_path.lower().endswith(".xlsx") or raw_data_path.lower().endswith(".xls"):
            df = pd.read_excel(raw_data_path)
        elif raw_data_path.lower().endswith(".csv"):
            df = pd.read_csv(raw_data_path)
        else:
            # Try Excel first by default
            df = pd.read_excel(raw_data_path)
        
        # Create normalized columns
        print("Normalizing text data...")
        
        # Normalize the slang/meme text
        def _row_lang(row):
            if 'Language' in df.columns:
                val = row.get('Language')
                if isinstance(val, str):
                    return val.lower()
            return 'both'

        df['Normalized_Text'] = df.apply(lambda row: normalize_text(
            row['Slang/Meme Text'],
            lang=_row_lang(row)
        ), axis=1)
        
        # Normalize the standard translation (for consistency)
        if 'Standard Translation' in df.columns:
            df['Normalized_Translation'] = df['Standard Translation'].apply(
                lambda x: normalize_text(x, lang='english') if isinstance(x, str) else x
            )
        
        # Save normalized dataset
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(f"Saving normalized dataset to {output_path}")
        try:
            df.to_excel(output_path, index=False)
        except PermissionError:
            # Fallback to CSV if the Excel file is locked/open
            csv_path = output_path.replace('.xlsx', '.csv')
            print(f"Excel file locked. Saving CSV fallback to {csv_path}")
            df.to_csv(csv_path, index=False)
        
        print("✅ Normalization completed successfully!")
        print(f"Original samples: {len(df)}")
        print("\nSample of normalized data:")
        for i in range(min(3, len(df))):
            print(f"Original: {df.iloc[i]['Slang/Meme Text']}")
            print(f"Normalized: {df.iloc[i]['Normalized_Text']}")
            print("---")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your dataset is at the correct path and has the right format.")

if __name__ == "__main__":
    normalize_dataset()