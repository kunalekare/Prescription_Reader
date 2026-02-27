Here is your complete **README.md file** in proper Markdown format.
You can copy this directly into your `README.md` file in GitHub.

---

```markdown
# 📄 Prescription Reader

An AI-powered **Prescription Reader System** that extracts text from medical prescriptions using **OCR (Optical Character Recognition)** and processes it using **NLP techniques** to generate structured medical information.

---

## 🚀 Project Overview

Medical prescriptions are often handwritten and difficult to interpret.  
This project aims to:

- 📸 Extract text from prescription images  
- 🧠 Improve recognition of handwritten medical text  
- 💊 Identify medicine names, dosage, and frequency  
- 📊 Convert unstructured prescription text into structured data  

This system can be used in:

- Hospitals  
- Pharmacies  
- Medical record digitization  
- Healthcare automation systems  

---

## 🏗️ Project Architecture
Input Image
    ↓
Image Preprocessing
    ↓
OCR Engine (Text Extraction)
    ↓
Text Cleaning & NLP Processing
    ↓
Medicine / Dosage Extraction
    ↓
Structured Output (JSON / CSV)

---

## 🛠️ Technologies Used

- **Python**
- **OpenCV** – Image preprocessing
- **Tesseract OCR / Google Vision API**
- **NLP (spaCy / Regex / Custom Model)**
- **Machine Learning (Optional for improvement)**

---

## 📂 Project Structure

```

Prescription_Reader/
│
├── notebooks/           # Experimentation & model training
├── src/                 # Core source code
├── requirements.txt     # Project dependencies
├── README.md            # Project documentation
└── .gitignore

````

---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/kunalekare/Prescription_Reader.git
cd Prescription_Reader
````

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

### Step 1: Provide Prescription Image

Place the prescription image inside the project folder.

### Step 2: Run OCR Script

```bash
python src/main.py
```

### Step 3: Output

The system will generate:

* Extracted text
* Identified medicines
* Dosage details
* Structured output format

---

## 🔍 Features

✔ Handwritten Prescription OCR
✔ Text Preprocessing
✔ Medicine Name Detection
✔ Dosage & Frequency Extraction
✔ Structured Data Output

---

## 📊 Future Improvements

* Train custom OCR model for medical handwriting
* Improve accuracy using Transformer-based NLP
* Add Web Interface (Flask / FastAPI)
* Integrate with Hospital Management System
* Deploy using Docker / Cloud

---

## 🎯 Challenges

* Poor handwriting recognition
* Abbreviations in prescriptions
* Medical terminology variations
* Image noise and blur

---

## 📈 Expected Accuracy

* Printed Text: High Accuracy
* Handwritten Text: Moderate (Can improve with custom training)

---

## 🤝 Contribution

Contributions are welcome!

1. Fork the repository
2. Create a new branch
3. Commit changes
4. Submit Pull Request

---



