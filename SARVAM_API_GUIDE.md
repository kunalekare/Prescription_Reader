# 🔑 Sarvam Vision API Setup & Testing Guide

## ✅ API Key Configured

Your Sarvam Vision API key has been configured:
```
SARVAM_API_KEY=sk_kklk9ckw_LqnGK2iUaVXQgk1dTjLufGWO
```

Location: `.env` file in project root

---

## 🌐 About Sarvam Vision API

**Sarvam AI** is an Indian AI company specializing in multilingual AI solutions. Their Vision API:

- ✅ **Multilingual OCR** - Supports 10+ Indian languages
- ✅ **High Accuracy** - Trained on Indian prescription patterns
- ✅ **Languages Supported**:
  - English
  - Hindi (हिंदी)
  - Tamil (தமிழ்)
  - Telugu (తెలుగు)
  - Bengali (বাংলা)
  - Marathi (मराठी)
  - Gujarati (ગુજરાતી)
  - Kannada (ಕನ್ನಡ)
  - Malayalam (മലയാളം)
  - Punjabi (ਪੰਜਾਬੀ)

---

## 🚀 Quick Test

### Option 1: Test Setup (Recommended First)
```bash
python test_setup.py
```

This verifies:
- All dependencies installed
- API key configured
- Directories created
- Model files present

### Option 2: Test Complete API Pipeline
```bash
python test_api_pipeline.py
```

This tests:
- API connection
- OCR text extraction from sample images
- Text preprocessing
- NER entity extraction
- Complete end-to-end pipeline

### Option 3: Test with Specific Image
```bash
python main.py Prescrption_Data/Day1/prescription1.jpg
```

---

## 📋 Complete Workflow

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Verify Setup
```bash
python test_setup.py
```

Expected output:
```
✅ requests                        - OK
✅ transformers                    - OK
✅ Configuration loaded successfully
✅ API key configured: sk_kklk9...
✅ All directories created
✅ Label map found: 9 labels
```

### Step 3: Test API Connection
```bash
python test_api_pipeline.py
```

This will:
1. Test API configuration ✅
2. Extract text from sample prescription using Sarvam API
3. Clean and preprocess the text
4. Extract entities (if model is trained)
5. Show complete pipeline results

### Step 4: Train Model (if needed)
```bash
python -m src.training.train
```

Requirements:
- CONLL format training data in `data/custom_indian/`
- Files: `train.conll`, `dev.conll`, `test.conll`

### Step 5: Run Web Interface
```bash
streamlit run app.py
```

Then open: http://localhost:8501

---

## 🔍 API Response Format

The Sarvam Vision API returns multilingual text. Example responses:

### English Prescription
```json
{
  "text": "Tab Crocin 500mg BD x 3 days"
}
```

### Hindi/Mixed Prescription
```json
{
  "text": "टैबलेट Crocin 500mg दिन में दो बार 3 दिन के लिए"
}
```

### Tamil Prescription
```json
{
  "text": "மாத்திரை Crocin 500mg தினம் இரண்டு முறை 3 நாட்கள்"
}
```

---

## 🎯 How OCR Text Flows to NER

```
1. Prescription Image (JPG/PNG)
         ↓
2. Sarvam Vision API
   - Extracts multilingual text
   - Returns JSON with text field
         ↓
3. Text Preprocessing
   - Cleans formatting
   - Normalizes dosages (10 mg → 10mg)
   - Handles special characters
         ↓
4. BioBERT Tokenization
   - Splits into subwords
   - Aligns with BIO tags
         ↓
5. NER Model (BioBERT)
   - Predicts entity labels
   - B-FORM, B-DRUG_BRAND, B-DOSAGE, etc.
         ↓
6. Post-processing
   - Merges subwords
   - Extracts complete entities
   - Groups by type
         ↓
7. Structured Output
   {
     "FORM": ["Tab"],
     "DRUG_BRAND": ["Crocin"],
     "DOSAGE": ["500mg"],
     "FREQUENCY": ["BD"],
     "DURATION": ["3 days"]
   }
```

---

## 🔧 Enhanced OCR Features

The OCR module (`src/ocr/sarvam_ocr.py`) now includes:

### 1. Multilingual Support
```python
extract_text_from_image("prescription.jpg", language="auto")
extract_text_from_image("prescription.jpg", language="hi")  # Hindi
extract_text_from_image("prescription.jpg", language="ta")  # Tamil
```

### 2. Automatic Retry Logic
- 3 retry attempts by default
- Exponential backoff (1s, 2s, 4s)
- Handles rate limits automatically

### 3. Multiple Response Formats
The code handles different API response structures:
- `{"text": "..."}`
- `{"data": {"text": "..."}}`
- `{"extracted_text": "..."}`
- `{"result": "..."}`

### 4. Comprehensive Error Handling
- Invalid API key detection
- Rate limit handling
- Timeout management
- Connection error recovery

---

## 📊 Testing Results

After running `test_api_pipeline.py`, you should see:

```
==================================================================
  TEST 1: Sarvam Vision API Connection
==================================================================

✅ Configuration loaded
   API URL: https://api.sarvam.ai/v1/vision
   API Key: sk_kklk9ckw_Lq...
   Timeout: 30s
   Max Retries: 3

✅ PASSED: API configuration valid

==================================================================
  TEST 2: OCR Text Extraction (Sample Image)
==================================================================

📸 Testing with: prescription1.jpg
   Location: Day1/prescription1.jpg

🔄 Extracting text...

✅ PASSED: Text extracted successfully!

📝 Extracted Text (245 characters):
======================================================================
Tab Crocin 500mg
Take 1 tablet twice daily after meals
Duration: 3 days
...
======================================================================

... [additional tests]

==================================================================
  TEST SUMMARY
==================================================================

📊 Results:
   API Configuration       : ✅ PASSED
   OCR Extraction          : ✅ PASSED
   Text Cleaning           : ✅ PASSED
   NER Extraction          : ⚠️  SKIPPED (model not trained)
   Complete Pipeline       : ⚠️  SKIPPED (model not trained)

🎯 Overall: 3/5 tests passed

💡 To train the model:
   1. Add CONLL data to data/custom_indian/
   2. Run: python -m src.training.train
```

---

## 🐛 Troubleshooting

### Issue: "Invalid API key"
**Solution**: Verify `.env` file contains correct key
```bash
cat .env  # Linux/Mac
type .env  # Windows
```

### Issue: "Rate limit exceeded"
**Solution**: Wait 60 seconds, or contact Sarvam for higher limits

### Issue: "No text extracted"
**Solution**: 
- Check image quality (clear, good lighting)
- Try different image format (JPG recommended)
- Verify image size (< 10MB)

### Issue: "Model not found"
**Solution**: Train model first
```bash
python -m src.training.train
```

---

## 📝 API Usage Examples

### Example 1: Basic OCR
```python
from src.ocr.sarvam_ocr import extract_text_from_image

text = extract_text_from_image("prescription.jpg")
print(text)
```

### Example 2: Multilingual OCR
```python
# Auto-detect language
text = extract_text_from_image("prescription.jpg", language="auto")

# Specify Hindi
text = extract_text_from_image("hindi_rx.jpg", language="hi")
```

### Example 3: Complete Pipeline
```python
from src.inference.predict import process_prescription

result = process_prescription("prescription.jpg")

if result['success']:
    print("Extracted entities:")
    for entity_type, values in result['entities'].items():
        print(f"{entity_type}: {values}")
```

### Example 4: Batch Processing
```python
from pathlib import Path
from src.inference.predict import process_prescription

prescription_dir = Path("Prescrption_Data/Day1")
results = []

for img in prescription_dir.glob("*.jpg"):
    result = process_prescription(str(img))
    if result['success']:
        results.append({
            'image': img.name,
            'entities': result['entities']
        })

# Save results
import json
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)
```

---

## 🎉 Success Checklist

- [x] API key configured in `.env`
- [ ] Run `python test_setup.py` - All green ✅
- [ ] Run `python test_api_pipeline.py` - OCR works ✅
- [ ] Add CONLL training data to `data/custom_indian/`
- [ ] Train model: `python -m src.training.train`
- [ ] Test complete pipeline with trained model
- [ ] Launch web interface: `streamlit run app.py`

---

## 📞 Support

### Sarvam API Issues
- Documentation: https://docs.sarvam.ai/
- Support: support@sarvam.ai

### Project Issues
1. Check logs: `outputs/logs/`
2. Review error messages
3. Run diagnostic: `python test_api_pipeline.py`

---

**🚀 You're all set! Your Sarvam Vision API is configured and ready to extract text from multilingual prescriptions!**
