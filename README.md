# 📄 Prescription Reader

An AI-powered **Prescription Reader System** that extracts text from medical prescriptions using **OCR (Optical Character Recognition)** and processes it using a fine-tuned **BioBERT NER model** to generate structured medical information and automatically fetch context for prescribed medicines.

---

## 🚀 Project Overview

Medical prescriptions are often handwritten and difficult to interpret. This system digitizes them with high accuracy by automating the extraction pipeline:
- 📸 **OCR Extraction:** Digitizes handwritten/printed prescription texts via OCR (Sarvam AI).
- 🧠 **NER Extraction:** Uses a fine-tuned BioBERT model designed specifically for medical Entity Recognition.
- 💊 **Entity Detection:** Accurately identities `DRUG`, `DOSAGE`, `FREQUENCY`, and `DURATION` entities.
- 📖 **Smart Drug Lookups:** Automatically queries Wikipedia to fetch medical descriptions for the exact medicine extracted.
- 💻 **Interactive UI:** Provides a clean, modern web application via Streamlit.

---

## 🛠️ Technologies Used

- **Python**
- **Streamlit** – Web application interface
- **Sarvam AI Vision API** – OCR Engine
- **Hugging Face Transformers / PyTorch** – Fine-tuned `Bio_ClinicalBERT` model for NER
- **Wikipedia API** – Automated drug/medication description lookup

---

## 📂 Project Structure

```text
Prescription_Reader/
│
├── src/                 # Core source code (OCR, Preprocessing, NER Inference)
├── models/              # Fine-tuned BioBERT model weights, cache & label maps
├── notebooks/           # Jupyter notebooks for model training (Colab)
├── data/                # Custom prescription dataset (CoNLL format)
├── app.py               # Streamlit web application
├── main.py              # Command-line testing script
└── requirements.txt     # Python dependencies
```

---

## ⚙️ Installation

### 1️⃣ Clone the Repository & Configure API Keys

```bash
git clone https://github.com/kunalekare/Prescription_Reader.git
cd Prescription_Reader
```
*Note: Make sure to place your `SARVAM_API_KEY` inside a local `.env` file first.*

### 2️⃣ Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

### 🌐 Option 1: The Web Interface (Recommended)
Launch the interactive browser-based visual UI where you can easily upload images and view extracted data dynamically:
```bash
streamlit run app.py
```

### 💻 Option 2: Command Line Interface
To run a quick execution on a single prescription image straight from your terminal:
```bash
python main.py path/to/sample_prescription.jpg
```

---

## 🤝 Contribution
Contributions to improve handwriting recognition or medicine mapping are welcome!
1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Submit a Pull Request
