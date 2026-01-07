# Cross-Language Meme & Slang Translator

**MCA Semester 1 NLP Project**

**Author:** Neeraj Negi ([@neeraj214](https://github.com/neeraj214))  
**Institution:** [Your University Name]  
**Department:** Department of Computer Science / MCA

---

## 📌 Project Overview

This project is a specialized Natural Language Processing (NLP) application designed to bridge the communication gap between informal internet slang/meme culture and standard English. It utilizes fine-tuned **T5 (Text-to-Text Transfer Transformer)** models to perform bidirectional translation.

### Key Features
- **Forward Translation:** Converts Internet Slang, Memes, and Hinglish into Standard English.
- **Reverse Translation:** Converts Standard English into Slang/Meme-style text.
- **Hinglish Support:** Specialized normalization and translation for code-mixed Hindi-English (Hinglish).
- **Web Interface:** Interactive UI built with **Streamlit** for real-time translation.
- **API/Deployment Ready:** Dockerized application structure for cloud deployment.

---

## 🛠️ Tech Stack

- **Language:** Python 3.11
- **Deep Learning Framework:** PyTorch, Hugging Face Transformers
- **Model Architecture:** FLAN-T5 / T5-Small (Fine-tuned)
- **Web Framework:** Streamlit
- **Data Processing:** Pandas, NumPy
- **Evaluation Metrics:** SacreBLEU, Custom Style Metrics

---

## 🚀 How to Run

### 1. Clone the Repository
```bash
git clone https://github.com/neeraj214/cross-language-meme-slang-translator.git
cd cross-language-meme-slang-translator
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run app.py
```
Access the app at `http://localhost:8501`.

---

## 🐳 Docker Deployment

To run using Docker:

```bash
docker build -t slang-translator .
docker run -p 8501:8501 slang-translator
```

---

## 📂 Project Structure

```
├── app.py                   # Main Streamlit Application
├── scripts/                 # Training, Preprocessing & Eval Scripts
│   ├── t5_training_forward.py
│   ├── preprocess_slang.py
│   └── ...
├── dataset/                 # Dataset & Dictionaries
├── results/metrics/         # BLEU Scores & Evaluation Logs
├── Dockerfile               # Container Configuration
├── requirements.txt         # Python Dependencies
└── README.md                # Project Documentation
```

---

## 📊 Performance

- **Forward BLEU Score:** ~65.4 (SacreBLEU)
- **Training Strategy:** Curriculum Learning (Easy → Hard samples)
- **Evaluation:** Multi-reference validation to handle diverse slang interpretations.

---

*Submitted as part of the MCA Semester 1 Curriculum.*
