# Contradicta

An AI-powered web app that analyzes healthcare text for contradictions and misleading claims.

---

## Quick Start

```bash
1. Install dependencies
pip install -r requirements.txt

2. (OCR only) Install Tesseract binary
   Ubuntu/Debian:  sudo apt install tesseract-ocr
   macOS:          brew install tesseract
   Windows:        https://github.com/UB-Mannheim/tesseract/wiki

3. Run the app
streamlit run app.py
```

---

## How It Works

| Step | What happens |
|------|-------------|
| **Input** | User pastes text OR uploads an image |
| **OCR** | `pytesseract` extracts text from images |
| **Sentence Split** | Regex splits text into individual claims |
| **NLI Classification** | `facebook/bart-large-mnli` classifies every sentence pair as *entailment / neutral / contradiction* |
| **Scoring** | Credibility score starts at 100, deducted per contradiction found |
| **Output** | Claims list, highlighted contradiction pairs, final score |

---

## Tech Stack

- **Frontend**: Streamlit
- **NLI Model**: `facebook/bart-large-mnli` (HuggingFace Transformers)
- **OCR**: pytesseract + Pillow
- **Language**: Python 3.10+

---

## Notes

- First run downloads the BART model (~1.6 GB). Subsequent runs use the cache.
- For GPU: change `device=-1` to `device=0` in `load_nli_model()` inside `app.py`.
