# Cross-Language Meme & Slang Translator

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Framework](https://img.shields.io/badge/Framework-Streamlit-red?logo=streamlit&logoColor=white)
![Model](https://img.shields.io/badge/Model-FLAN--T5-orange?logo=huggingface&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-success)

**MCA Semester 1 NLP Project**  
**Author:** Neeraj Negi ([@neeraj214](https://github.com/neeraj214))  
**Institution:** Graphic Era Hill University  
**Department:** Department of Computer Science / MCA

---

## 📌 Project Overview

**Cross-Language Meme & Slang Translator** is a specialized Natural Language Processing (NLP) application designed to bridge the communication gap between informal internet slang/meme culture and standard English. 

Traditional translators (like Google Translate) often fail to capture the nuance of internet slang or code-mixed languages like **Hinglish**. This project utilizes fine-tuned **T5 (Text-to-Text Transfer Transformer)** models to perform accurate, bidirectional translation.

### ✨ Key Features

*   **🔄 Bidirectional Translation:**
    *   **Forward:** Internet Slang / Memes / Hinglish ➡️ Standard English
    *   **Reverse:** Standard English ➡️ Slang / Meme-style text
*   **🇮🇳 Hinglish Support:** specialized normalization pipeline for handling code-mixed Hindi-English text (e.g., *"kya scene hai bro"*).
*   **🖥️ Interactive UI:** A clean, real-time web interface built with **Streamlit**.
*   **🧠 Advanced Training:** Uses **Curriculum Learning** strategies to stabilize training on noisy datasets.
*   **🐳 Deployment Ready:** Fully Dockerized for easy deployment to cloud platforms like Render, Azure, or AWS.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.11 |
| **Deep Learning** | PyTorch, Hugging Face Transformers |
| **Model** | Google FLAN-T5 (Fine-tuned) |
| **Web Framework** | Streamlit |
| **Data Processing** | Pandas, NumPy, Regex |
| **Evaluation** | SacreBLEU (Multi-reference) |
| **Containerization** | Docker |

---

## 🔗 Live App

Streamlit Cloud: https://cross-language-meme-slang-translator-ntuaeasfjtwmonwyttnbtj.streamlit.app/

If you see a “no response” message briefly, wait a moment and refresh; initial cold start may download model weights.

---

## 🚀 Getting Started

### Prerequisites

*   Python 3.8+
*   Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/neeraj214/cross-language-meme-slang-translator.git
    cd cross-language-meme-slang-translator
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    streamlit run app.py
    ```
    The app will open in your browser at `http://localhost:8501`.

---

## 🐳 Docker Usage

To run the application in an isolated container:

1.  **Build the image:**
    ```bash
    docker build -t slang-translator .
    ```

2.  **Run the container:**
    ```bash
    docker run -p 8501:8501 slang-translator
    ```

---

## � Model Performance

We evaluated the model using **SacreBLEU**, utilizing a multi-reference test set to account for the diversity of valid slang translations.

| Metric | Score | Notes |
| :--- | :--- | :--- |
| **Forward BLEU** | **~65.4** | Slang → English |
| **Reverse BLEU** | **~42.1** | English → Slang (High diversity) |

**Training Strategy:**
*   **Curriculum Learning:** The model was first trained on "easy" (short) samples before moving to complex, noisy sentences.
*   **Multi-Reference Evaluation:** Validated against multiple acceptable translations for fairness.

---

## �📂 Project Structure

```bash
cross-language-meme-slang-translator/
├── app.py                   # 📱 Main Streamlit Application
├── dataset/                 # 💾 Raw and processed datasets
│   ├── slang_emoji_dict.py  # Dictionary for emoji/slang mapping
│   └── ...
├── scripts/                 # ⚙️ Helper scripts
│   ├── t5_training_forward.py   # Training pipeline
│   ├── preprocess_slang.py      # Data cleaning & normalization
│   └── evaluate_bleu.py         # Metric calculation
├── results/                 # 📈 Evaluation logs and metrics
├── Dockerfile               # 🐳 Docker configuration
├── requirements.txt         # 📦 Dependencies
└── README.md                # 📄 Documentation
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/YourFeature`).
3.  Commit your changes (`git commit -m 'Add some feature'`).
4.  Push to the branch (`git push origin feature/YourFeature`).
5.  Open a Pull Request.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
<div align="center">
  <sub>Built with ❤️ by <a href="https://github.com/neeraj214">Neeraj Negi</a> as part of the MCA Curriculum.</sub>
</div>
