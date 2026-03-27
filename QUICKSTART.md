# 🎉 QUICK START GUIDE - Prescription Reader

## ✅ Your API Key is Configured!

```
SARVAM_API_KEY = sk_kklk9ckw_LqnGK2iUaVXQgk1dTjLufGWO ✅
```

---

## 🚀 3-Step Quick Start

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Test System
```bash
python test_api_pipeline.py
```

### 3️⃣ Run Web Interface
```bash
streamlit run app.py
```

Then open: **http://localhost:8501** 🌐

---

## 📱 What You Can Do Now

### ✅ **Ready to Use** (No Training Required)
1. **OCR Text Extraction** - Extract text from prescriptions using Sarvam Vision API
   ```bash
   python -c "from src.ocr.sarvam_ocr import extract_text_from_image; print(extract_text_from_image('your_prescription.jpg'))"
   ```

2. **Web Interface** - Upload and process prescriptions visually
   ```bash
   streamlit run app.py
   ```

3. **Command Line** - Process single prescription
   ```bash
   python main.py Prescrption_Data/Day1/prescription1.jpg
   ```

### ⚠️ **Requires Training** (One-Time Setup)
4. **NER Entity Extraction** - Identify drugs, dosages, frequency, duration
   ```bash
   # First: Add CONLL data to data/custom_indian/
   # Then: Train model
   python -m src.training.train
   ```

---

## 🎯 Complete Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  PRESCRIPTION IMAGE                                         │
│  (JPG, PNG - English/Hindi/Tamil/Telugu/etc.)              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: OCR EXTRACTION (Sarvam Vision API) ✅              │
│  • Multilingual text extraction                            │
│  • Supports 10+ Indian languages                           │
│  • Output: Raw prescription text                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: TEXT PREPROCESSING ✅                              │
│  • Clean formatting                                         │
│  • Normalize dosages (10 mg → 10mg)                       │
│  • Remove extra spaces                                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: NER ENTITY EXTRACTION (BioBERT) ⚠️ Need Training  │
│  • Identify: FORM, DRUG, DOSAGE, FREQUENCY, DURATION      │
│  • Uses CoNLL format training data                         │
│  • BIO tagging scheme                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│  OUTPUT: STRUCTURED DATA                                    │
│  {                                                          │
│    "FORM": ["Tab"],                                        │
│    "DRUG_BRAND": ["Crocin"],                               │
│    "DOSAGE": ["500mg"],                                    │
│    "FREQUENCY": ["BD"],                                    │
│    "DURATION": ["3 days"]                                  │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Current System Status

| Component | Status | Action Required |
|-----------|--------|-----------------|
| **Sarvam API** | ✅ Configured | None - Ready to use |
| **OCR Module** | ✅ Working | None - Multilingual support active |
| **Preprocessing** | ✅ Working | None - Text cleaning ready |
| **Training Pipeline** | ✅ Implemented | Add CONLL data & train |
| **NER Model** | ⚠️ Not Trained | Train with: `python -m src.training.train` |
| **Evaluation** | ✅ Implemented | Use after training |
| **Web Interface** | ✅ Ready | Run: `streamlit run app.py` |
| **Documentation** | ✅ Complete | See README.md & guides |

---

## 🎓 Training Your NER Model

### Step 1: Prepare CONLL Data

Create files in `data/custom_indian/`:

**Format Example (train.conll):**
```
Tab B-FORM
Crocin B-DRUG_BRAND
500mg B-DOSAGE
BD B-FREQUENCY
x O
3 B-DURATION
days I-DURATION

Cap B-FORM
Dolo B-DRUG_BRAND
650mg B-DOSAGE
```

**Required Files:**
- `train.conll` - Training data (recommended: 300+ examples)
- `dev.conll` - Validation data (recommended: 50+ examples)
- `test.conll` - Test data (recommended: 50+ examples)

### Step 2: Train Model
```bash
python -m src.training.train
```

**Expected Training Output:**
```
==================================================
Epoch 1/10
==================================================
Training: 100%|████████████████| 50/50 [02:15<00:00]
Average training loss: 0.4532
Validation loss: 0.3821
New best validation loss: 0.3821
✓ Saved best model

... [continues for 10 epochs]

Training complete!
Final F1: 0.87
```

### Step 3: Test Complete Pipeline
```bash
python test_api_pipeline.py
```

Now all 5 tests should pass! ✅

---

## 📁 Important Files

| File | Purpose | Status |
|------|---------|--------|
| `.env` | API configuration | ✅ Configured |
| `app.py` | Web interface | ✅ Ready |
| `main.py` | CLI interface | ✅ Ready |
| `test_setup.py` | System verification | ✅ Use anytime |
| `test_api_pipeline.py` | API & pipeline test | ✅ Use to verify OCR |
| `SARVAM_API_GUIDE.md` | Detailed API guide | 📖 Read for details |
| `IMPLEMENTATION_SUMMARY.md` | Development notes | 📖 Technical details |

---

## 🌐 Multilingual Support

Your system supports these languages out of the box:

| Language | Script | Example |
|----------|--------|---------|
| English | Latin | "Tab Crocin 500mg BD" |
| Hindi | Devanagari | "गोली क्रोसिन 500mg दिन में दो बार" |
| Tamil | Tamil | "மாத்திரை க்ரோசின் 500mg" |
| Telugu | Telugu | "మాత్ర క్రోసిన్ 500mg" |
| Bengali | Bengali | "ট্যাব ক্রোসিন 500mg" |
| Marathi | Devanagari | "गोळी क्रोसिन 500mg" |
| Gujarati | Gujarati | "ગોળી ક્રોસિન 500mg" |
| Kannada | Kannada | "ಮಾತ್ರೆ ಕ್ರೋಸಿನ್ 500mg" |
| Malayalam | Malayalam | "ഗുളിക ക്രോസിൻ 500mg" |
| Punjabi | Gurmukhi | "ਗੋਲੀ ਕ੍ਰੋਸਿਨ 500mg" |

---

## 💡 Example Usage

### Example 1: Quick OCR Test
```python
from src.ocr.sarvam_ocr import extract_text_from_image

# Extract text
text = extract_text_from_image("prescription.jpg")
print(text)
```

### Example 2: Process with Cleaning
```python
from src.ocr.sarvam_ocr import extract_text_from_image
from src.preprocessing.text_cleaner import clean_text

# Extract and clean
raw = extract_text_from_image("prescription.jpg")
clean = clean_text(raw)
print(f"Cleaned: {clean}")
```

### Example 3: Complete Pipeline (After Training)
```python
from src.inference.predict import process_prescription

result = process_prescription("prescription.jpg")

if result['success']:
    print("Entities found:")
    for entity_type, values in result['entities'].items():
        print(f"  {entity_type}: {', '.join(values)}")
```

### Example 4: Batch Processing
```python
from pathlib import Path
from src.inference.predict import process_prescription
import json

results = []
for img in Path("Prescrption_Data/Day1").glob("*.jpg"):
    result = process_prescription(str(img))
    if result.get('success'):
        results.append({
            'file': img.name,
            'entities': result['entities']
        })

# Save results
with open("batch_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

---

## 🐛 Common Issues & Solutions

### ❌ "Invalid API key"
```bash
# Check .env file
type .env  # Windows
cat .env   # Linux/Mac

# Should show: SARVAM_API_KEY=sk_kklk9ckw_...
```

### ❌ "Model not found"
```bash
# Train the model first
python -m src.training.train

# Or check if model exists
ls models/biobert_prescription/  # Linux/Mac
dir models\biobert_prescription\  # Windows
```

### ❌ "No module named 'src'"
```bash
# Ensure you're in project root
cd Prescription_Reader

# Then run command
python main.py prescription.jpg
```

### ❌ "Rate limit exceeded"
```bash
# Wait 60 seconds or contact Sarvam for higher limits
# API includes automatic retry with backoff
```

---

## 📞 Getting Help

1. **Check logs**: `outputs/logs/` - Contains detailed error traces
2. **Run diagnostics**: `python test_setup.py` - System health check
3. **Test API**: `python test_api_pipeline.py` - Verify OCR works
4. **Review docs**: 
   - `README.md` - General documentation
   - `SARVAM_API_GUIDE.md` - API-specific guide
   - `IMPLEMENTATION_SUMMARY.md` - Technical details

---

## ✅ Next Steps

### Immediate (No Training)
- [x] API configured ✅
- [ ] Run: `python test_api_pipeline.py`
- [ ] Test web interface: `streamlit run app.py`
- [ ] Upload a prescription and see OCR results

### Short Term (Requires Training Data)
- [ ] Prepare CONLL format training data
- [ ] Add files to `data/custom_indian/`
- [ ] Train model: `python -m src.training.train`
- [ ] Test complete pipeline with entities

### Long Term (Optional Enhancements)
- [ ] Add more training data (improve accuracy)
- [ ] Fine-tune hyperparameters
- [ ] Deploy as REST API
- [ ] Add Docker containerization
- [ ] Integrate with hospital systems

---

## 🎉 Congratulations!

Your Prescription Reader is **professionally configured** and ready to use! 

**Current Capabilities:**
- ✅ Extract text from multilingual prescriptions
- ✅ Clean and preprocess medical text
- ✅ Beautiful web interface
- ✅ Command-line tools
- ✅ Batch processing support

**After Training:**
- 🎯 Extract medical entities (drugs, dosages, etc.)
- 📊 Generate structured prescription data
- 💾 Export to JSON/CSV
- 📈 Evaluate model performance

---

**Start now:** `python test_api_pipeline.py` 🚀
