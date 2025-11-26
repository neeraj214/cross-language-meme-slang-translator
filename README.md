# Slang/Meme Translator

This project translates between internet slang/meme language and standard English using fine-tuned T5 models.

## Features

- **Forward Translation**: Convert slang/meme text to standard English
- **Reverse Translation**: Convert standard English to slang/meme text
- **Interactive Demo**: Streamlit web interface for easy translation
- **Performance Metrics**: BLEU scores and style metrics display

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## Model Training

The project uses two fine-tuned T5 models:

1. **Forward Model**: Translates from slang/meme to standard English
   - Checkpoint directory: `outputs/checkpoints/t5-small-forward-ep5-lr3e4-64`

2. **Reverse Model**: Translates from standard English to slang/meme
   - Checkpoint directory: `outputs/checkpoints/t5-small-reverse-ep5-lr3e4-64`

## Evaluation Metrics

- **BLEU Scores**: Measures translation quality against reference translations
- **Style Metrics**: Evaluates emoji presence, slang presence, and lexical diversity

## Project Structure

- `app.py`: Streamlit demo application
- `scripts/`: Training and evaluation scripts
- `outputs/checkpoints/`: Saved model checkpoints
- `results/metrics/`: Evaluation metrics
- `dataset/`: Training data and dictionaries