# ✅ COMPLETE TEXT EXTRACTION SETUP

## 🚀 **Quick Start - One Command!**

**Just run this:**
```bash
python test_complete_extraction.py
```

OR double-click: **`run_extraction_test.bat`**

This script will:
- ✅ Auto-install Sarvam SDK if missing
- ✅ Verify API key configuration
- ✅ Find a test prescription image
- ✅ Extract text using Document Intelligence API
- ✅ Display extracted text
- ✅ Save results to file

---

## 📋 What It Does

The extraction process follows these steps:

### 1. **Install Dependencies**
```bash
pip install sarvamai
```

### 2. **Initialize Client**
```python
from sarvamai import SarvamAI
client = SarvamAI(api_subscription_key="your_key")
```

### 3. **Create & Process Job**
```python
# Create job
job = client.document_intelligence.create_job(
    language="hi-IN",
    output_format="md"
)

# Upload image
job.upload_file("prescription.jpg")

# Start processing
job.start()

# Wait for completion (10-30 seconds)
status = job.wait_until_complete()

# Download results
job.download_output("output.zip")
```

### 4. **Extract & Display Text**
- Unzips the output
- Reads the markdown/text file
- Displays extracted text
- Saves to `outputs/extracted_text_[job_id].txt`

---

## 📦 Files Created for You

### Core Files:
1. **`test_complete_extraction.py`** - Complete extraction test script
2. **`run_extraction_test.bat`** - One-click runner
3. **`src/ocr/sarvam_ocr_new.py`** - New OCR module with Document Intelligence

### Documentation:
4. **`README_FIX.md`** - Quick 3-step fix guide
5. **`SARVAM_FIXED.md`** - Complete technical details
6. **`THIS FILE`** - Complete extraction guide

---

## 🎯 Expected Output

When you run `test_complete_extraction.py`, you'll see:

```
======================================================================
  PRESCRIPTION TEXT EXTRACTION TEST
======================================================================

Step 1: Checking Sarvam SDK installation...
✅ Sarvam SDK is installed

Step 2: Checking API key configuration...
✅ API key found: sk_kklk9ckw_LqnGK...

Step 3: Initializing Sarvam client...
✅ Client initialized successfully

Step 4: Looking for test prescription image...
✅ Using test image: Prescrption_Data\Day1-5\image1.jpg

Step 5: Extracting text using Document Intelligence API...
⏳ This may take 10-30 seconds...

   Creating job...
   ✅ Job created: job_abc123
   Uploading image...
   ✅ Image uploaded
   Starting processing...
   ✅ Processing started
   ⏳ Waiting for completion...
   ✅ Job completed in 18.45 seconds
   Status: succeeded

   Downloading results...
   ✅ Downloaded output ZIP
   📂 Extracted files:
      - output.md

======================================================================
  ✅ TEXT EXTRACTION SUCCESSFUL!
======================================================================

📝 Extracted Text (245 characters):
----------------------------------------------------------------------
Tab Crocin 500mg
BD x 3 days

Syrup Ambrodil 5ml
TDS x 5 days
----------------------------------------------------------------------

💾 Saved to: outputs\extracted_text_job_abc123.txt

======================================================================
  🎉 TEXT EXTRACTION COMPLETE!
======================================================================

Next steps:
1. Try the web demo: streamlit run demo_ocr.py
2. Test more images with different prescriptions
3. Train NER model to extract drug names, dosages, etc.
```

---

## ⏱️ Processing Time

| Image Size | Expected Time |
|------------|---------------|
| < 1MB      | ~10 seconds   |
| 1-5MB      | ~20 seconds   |
| 5-10MB     | ~30 seconds   |

**Note:** First request might take longer as the API initializes.

---

## 🔧 Troubleshooting

### Error: "sarvamai module not found"
**Solution:** The script auto-installs it, or run:
```bash
pip install sarvamai
```

### Error: "API key not found"
**Solution:** Check `.env` file contains:
```
SARVAM_API_KEY=sk_kklk9ckw_LqnGK2iUaVXQgk1dTjLufGWO
```

### Error: "No test image found"
**Solution:** The script will ask you to provide an image path. Enter:
```
Prescrption_Data\Day1-5\your_image.jpg
```

### Error: "Job failed"
**Possible causes:**
- Invalid image file
- Image too large (> 10MB)
- API key expired
- Network connection issue

**Solution:** Check error message and try different image.

---

## 🎨 Using in Your Code

### Simple Text Extraction:
```python
from sarvamai import SarvamAI
import tempfile
import zipfile
from pathlib import Path

api_key = "sk_kklk9ckw_LqnGK2iUaVXQgk1dTjLufGWO"
client = SarvamAI(api_subscription_key=api_key)

# Create and run job
job = client.document_intelligence.create_job(
    language="hi-IN",
    output_format="md"
)
job.upload_file("prescription.jpg")
job.start()
job.wait_until_complete()

# Download and extract
with tempfile.TemporaryDirectory() as temp_dir:
    output_path = Path(temp_dir) / "output.zip"
    job.download_output(str(output_path))
    
    extracted_dir = Path(temp_dir) / "extracted"
    extracted_dir.mkdir(exist_ok=True)
    
    with zipfile.ZipFile(output_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_dir)
    
    text_files = list(extracted_dir.glob("*.md"))
    with open(text_files[0], 'r', encoding='utf-8') as f:
        text = f.read()

print(f"Extracted: {text}")
```

### Using the Updated OCR Module:
**Once you copy `sarvam_ocr_new.py` → `sarvam_ocr.py`:**

```python
from src.ocr.sarvam_ocr import extract_text_from_image

# Simple usage
text = extract_text_from_image("prescription.jpg", language="hi-IN")
print(text)
```

---

## 📊 Supported Languages

All **23 Indian languages + English**:
- Hindi (hi-IN)
- Tamil (ta-IN)
- Telugu (te-IN)
- Bengali (bn-IN)
- Gujarati (gu-IN)
- Kannada (kn-IN)
- Malayalam (ml-IN)
- Marathi (mr-IN)
- Punjabi (pa-IN)
- Odia (od-IN)
- Assamese (as-IN)
- Urdu (ur-IN)
- And 11 more...

---

## 🎯 Next Steps After Successful Extraction

### 1. Test with Multiple Images
```bash
python test_complete_extraction.py
```
Try different prescriptions to verify accuracy.

### 2. Use Web Interface
```bash
streamlit run demo_ocr.py
```
User-friendly interface for uploading and extracting.

### 3. Train NER Model
Once OCR works, train the Named Entity Recognition model to extract:
- Drug names (brand & generic)
- Dosages (500mg, 10ml, etc.)
- Frequency (BD, TDS, OD)
- Duration (3 days, 1 week)

```bash
# Add CoNLL training data to data/custom_indian/
python -m src.training.train
```

### 4. Use Complete Pipeline
```bash
streamlit run app.py
```
Full system: OCR → Preprocessing → NER → Structured Output

---

## 🆘 Need Help?

### Check These Files:
- `README_FIX.md` - Quick fix guide
- `SARVAM_FIXED.md` - Technical details
- `FIX_404_ERROR.md` - Troubleshooting

### Contact Sarvam:
- Email: support@sarvam.ai
- Discord: https://discord.com/invite/5rAsykttcs
- Docs: https://docs.sarvam.ai

### Your API Key:
```
sk_kklk9ckw_LqnGK2iUaVXQgk1dTjLufGWO
```

---

## ✅ Run NOW!

```bash
python test_complete_extraction.py
```

This will extract text from a prescription and display the results!

**OR** just double-click: `run_extraction_test.bat`

🎉 **Text extraction complete!** 🎉
