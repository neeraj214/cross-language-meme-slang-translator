# Cross-Language Meme & Slang Translator

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Framework](https://img.shields.io/badge/Framework-FastAPI-009688?logo=fastapi&logoColor=white)
![Transformers](https://img.shields.io/badge/Library-Transformers-FF9D00?logo=huggingface&logoColor=white)
![Framework](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit&logoColor=white)
![Model](https://img.shields.io/badge/Model-FLAN--T5-orange?logo=huggingface&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-success)

**MCA Semester 1 NLP Project**  
**Author:** Neeraj Negi ([@neeraj214](https://github.com/neeraj214))  
**Institution:** Graphic Era Hill University  
**Department:** Department of Computer Science / MCA

---

## 📌 Overview

**Cross-Language Meme & Slang Translator** is a specialized Natural Language Processing (NLP) application designed to bridge the communication gap between informal internet slang/meme culture and standard English. 

Traditional translators often fail to capture the nuance of internet slang or code-mixed languages like **Hinglish**. This project utilizes fine-tuned **T5 (Text-to-Text Transfer Transformer)** models to perform accurate, bidirectional translation, catering to the evolving digital language landscape.

## ❓ Problem Statement

Internet communication is increasingly dominated by:
- **Gen-Z Slang**: "no cap", "fr fr", "rizz", etc.
- **Hinglish**: Code-mixed Hindi and English (e.g., "bhai kya scene hai").
- **Meme Culture**: Context-dependent phrases that lose meaning in literal translation.

Standard NMT (Neural Machine Translation) systems are trained on formal corpora (news, legal documents) and struggle with these informal, noisy, and rapidly changing linguistic patterns. This project addresses this gap by providing a specialized translation layer.

## 📊 Dataset

The project leverages a custom-curated dataset focused on informal communication:
- **Size**: ~1,000+ high-quality parallel sentence pairs.
- **Sources**: Custom-collected slang mappings, Hinglish datasets, and social media data.
- **Content**: Slang/Meme phrases paired with their standard English equivalents.
- **Processing**: Includes a specialized normalization pipeline for Hinglish and slang consistency.

## 🧠 Model Architecture

The system is built upon **Google's FLAN-T5-small**, a text-to-text transformer model.
- **Fine-tuning**: Bidirectional fine-tuning (Slang ↔ Standard English).
- **Prefix-based Tasks**: Uses task-specific prefixes like `translate english slang to english:` to guide the generation process.
- **Inference**: Optimized using Beam Search (num_beams=6) for better translation quality.

## 🚀 Training Pipeline

Our training strategy focuses on robustness and quality:
- **Curriculum Learning**: Training starts with "easy" (shorter) samples before progressing to complex, noisy sentences.
- **Hyperparameters**: Centralized configuration via `config.yaml` (Batch Size: 16, LR: 3e-5, Epochs: 6).
- **Optimization**: AdamW optimizer with weight decay and label smoothing (0.1) for better generalization.

## 📈 Evaluation Metrics

We employ a multi-metric evaluation strategy to capture different aspects of translation quality:
- **BLEU / SacreBLEU**: Measures n-gram overlap with reference translations.
- **ChrF**: Character n-gram F-score, useful for morphologically rich or noisy text.
- **BERTScore**: Captures semantic similarity using contextual embeddings.
- **Style Metrics**: Tracking slang and emoji density to ensure stylistic consistency in reverse translation.

| Metric | Score | Notes |
| :--- | :--- | :--- |
| **Forward BLEU** | **~20.56** | Slang/Hinglish → Standard English |
| **Reverse BLEU** | **~9.65** | Standard English → Slang (Higher diversity) |

## 🌐 API Deployment (FastAPI)

For production-grade use, the project includes a **FastAPI** backend:
- **Endpoint**: `/translate` (POST)
- **Schema**:
  ```json
  {
    "text": "that fit is fire",
    "direction": "forward"
  }
  ```
- **Features**: Async processing, health checks, and Pydantic validation.

## ✨ Example Results

| Input (Slang/Hinglish) | Output (Standard English) |
| :--- | :--- |
| "no cap, he's the goat" | "honestly, he is the greatest of all time" |
| "bhai kya entry maari 🔥" | "what an entry, bro!" |
| "bro’s cooked 💀" | "he messed up badly" |

## ⚠️ Limitations

- **Slang Evolution**: Internet slang changes rapidly; the model requires periodic retraining.
- **Context Sensitivity**: Some memes require deep cultural context that a small model may miss.
- **Noisy Inputs**: Highly unstructured or misspelled text can lead to hallucinated translations.

## 🔮 Future Improvements

- **Larger Models**: Moving to FLAN-T5-base or Large for better nuance.
- **Real-time Updates**: Integration with social media APIs to capture emerging slang.
- **Multi-modal Support**: Translating text within meme images.

## 🚀 Installation & Usage

### Prerequisites
- Python 3.11+
- Git

### Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/neeraj214/cross-language-meme-slang-translator.git
   cd cross-language-meme-slang-translator
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run Streamlit UI**:
   ```bash
   streamlit run app.py
   ```
4. **Run FastAPI Backend**:
   ```bash
   uvicorn backend.main:app --reload
   ```

## 📂 Folder Structure

```bash
cross-language-meme-slang-translator/
├── backend/                # 🌐 FastAPI production backend
├── training/               # 🚀 Training scripts and pipeline
├── evaluation/             # 📈 Evaluation scripts and metrics
├── data/                   # 💾 Raw and processed datasets
├── models/                 # 🧠 Saved model checkpoints
├── config/                 # ⚙️ YAML configuration files
├── docs/                   # 📄 Documentation and diagrams
├── results/                # 📊 Evaluation logs
├── app.py                  # 📱 Streamlit Application
├── config.yaml             # 🛠️ Centralized configuration
├── Dockerfile              # 🐳 Containerization
└── requirements.txt        # 📦 Dependencies
```

## 🤝 Contributing

Contributions are welcome! Please fork the repository and open a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
<div align="center">
  <sub>Built with ❤️ by <a href="https://github.com/neeraj214">Neeraj Negi</a></sub>
</div>
