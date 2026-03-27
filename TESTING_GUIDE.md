# 🧪 TESTING GUIDE - Verify Your System Works

## 🎯 3 Ways to Test

### ⚡ Option 1: Quick Command Line Test (Fastest)
```bash
python quick_test.py
```
**What it does:**
- ✅ Tests API configuration
- ✅ Finds a sample prescription image
- ✅ Calls Sarvam Vision API
- ✅ Shows extracted text in terminal

**Expected Output:**
```
============================================
  🔬 QUICK OCR API TEST
============================================

🔑 Testing API Configuration
✅ Configuration loaded successfully
   API Key: sk_kklk9ckw_LqnGK2i...
   
📸 Testing OCR Extraction
Image: prescription1.jpg

🔄 Calling Sarvam Vision API...

✅ SUCCESS! Text extracted

📝 Extracted Text (245 characters):
Tab Crocin 500mg
Take 1 tablet twice daily after meals
Duration: 3 days
...

✅ ALL TESTS PASSED!
🎉 Your Sarvam Vision API is working correctly!
```

---

### 🖥️ Option 2: Interactive Demo (Visual)
```bash
streamlit run demo_ocr.py
```
**What it does:**
- ✅ Opens web interface at http://localhost:8501
- ✅ Upload prescription images
- ✅ Click "Extract Text" button
- ✅ See results in real-time
- ✅ Download extracted text

**Screenshot Preview:**
```
┌─────────────────────────────────────────────────┐
│  🔬 OCR Demo - Sarvam API Test                  │
├─────────────────────────────────────────────────┤
│  ✅ API Key Configured                          │
│  Key: sk_kklk9ckw_LqnGK2i...                   │
│                                                  │
│  📋 Instructions:                                │
│  1. Upload a prescription image                 │
│  2. Click "Extract Text" button                 │
│  3. View extracted text                         │
│                                                  │
│  [Choose a prescription image]  [Browse...]     │
│                                                  │
│  ┌──────────────────┬──────────────────┐       │
│  │ 📸 Uploaded Image│ 📝 Extracted Text │       │
│  │                  │                   │       │
│  │   [Image Preview]│ [🚀 Extract Text] │       │
│  │                  │                   │       │
│  └──────────────────┴──────────────────┘       │
└─────────────────────────────────────────────────┘
```

---

### 🔄 Option 3: Complete Pipeline Test
```bash
python test_api_pipeline.py
```
**What it does:**
- ✅ Tests ALL system components
- ✅ API configuration
- ✅ OCR extraction
- ✅ Text preprocessing
- ✅ NER model (if trained)
- ✅ End-to-end pipeline

**Expected Output:**
```
============================================
  TEST 1: Sarvam Vision API Connection
============================================
✅ PASSED

============================================
  TEST 2: OCR Text Extraction
============================================
✅ PASSED: Text extracted successfully!

============================================
  TEST 3: Text Preprocessing
============================================
✅ PASSED: Text cleaned successfully!

============================================
  TEST 4: NER Entity Extraction
============================================
⚠️  SKIPPED: Model not trained yet

============================================
  TEST SUMMARY
============================================
📊 Results:
   API Configuration       : ✅ PASSED
   OCR Extraction          : ✅ PASSED
   Text Cleaning           : ✅ PASSED
   NER Extraction          : ⚠️  SKIPPED
   Complete Pipeline       : ⚠️  SKIPPED

🎯 Overall: 3/5 tests passed
```

---

## 🚀 One-Click Testing (Windows)

Just double-click:
```
run_demo.bat
```

This will:
1. ✅ Check system setup
2. ✅ Test API connection
3. ✅ Launch demo interface

---

## 🚀 One-Click Testing (Linux/Mac)

Make it executable and run:
```bash
chmod +x run_demo.sh
./run_demo.sh
```

---

## 📊 What Each Test Verifies

### Test 1: API Configuration ✅
**Checks:**
- `.env` file exists
- `SARVAM_API_KEY` is set
- API URL is correct
- Timeout settings configured

**Pass Criteria:**
- API key present and valid format

---

### Test 2: OCR Extraction ✅
**Checks:**
- Can connect to Sarvam API
- Can send image file
- Receives response
- Extracts text successfully

**Pass Criteria:**
- Text extracted (not empty)
- No API errors

---

### Test 3: Text Preprocessing ✅
**Checks:**
- Can clean extracted text
- Normalizes whitespace
- Standardizes dosage formats
- Handles special characters

**Pass Criteria:**
- Cleaned text is valid
- Proper formatting applied

---

### Test 4: NER Extraction ⚠️
**Checks:**
- Model files exist
- Can load BioBERT model
- Tokenization works
- Entity prediction works

**Pass Criteria:**
- Entities extracted successfully

**Note:** Requires trained model

---

### Test 5: Complete Pipeline ⚠️
**Checks:**
- All components work together
- Image → OCR → Clean → NER → Output
- JSON output format correct

**Pass Criteria:**
- End-to-end processing successful

**Note:** Requires trained model

---

## 🎯 Quick Start Testing Steps

### Step 1: Quick Sanity Check (30 seconds)
```bash
python quick_test.py
```
✅ Should show: "ALL TESTS PASSED!"

### Step 2: Visual Verification (2 minutes)
```bash
streamlit run demo_ocr.py
```
1. Upload any prescription image
2. Click "Extract Text"
3. Verify text appears

### Step 3: Full System Test (1 minute)
```bash
python test_api_pipeline.py
```
✅ Should pass 3/5 tests (OCR, preprocessing, config)
⚠️ 2 tests skipped (requires trained model)

---

## 📸 Sample Images for Testing

Your project includes sample prescriptions in:
```
Prescrption_Data/
├── Day 1/
├── Day 2/
├── Day 3/
├── Day 4/
└── Day 5/
```

**Recommended test images:**
- Clear, printed prescriptions ✅
- Good lighting ✅
- High resolution ✅

---

## 🐛 Troubleshooting Test Failures

### ❌ Test 1 Failed: "API Key Not Found"
**Solution:**
```bash
# Create .env file with your API key
echo "SARVAM_API_KEY=sk_kklk9ckw_LqnGK2iUaVXQgk1dTjLufGWO" > .env

# Verify it's there
type .env  # Windows
cat .env   # Linux/Mac
```

### ❌ Test 2 Failed: "Connection Error"
**Solutions:**
1. Check internet connection
2. Verify API key is correct
3. Try again (may be temporary network issue)

### ❌ Test 2 Failed: "Invalid API Key"
**Solutions:**
1. Double-check API key in .env
2. Ensure no extra spaces
3. Contact Sarvam for key verification

### ❌ Test 2 Failed: "Rate Limit Exceeded"
**Solutions:**
1. Wait 60 seconds
2. Contact Sarvam for higher limits

### ❌ Test 2 Failed: "No Text Extracted"
**Solutions:**
1. Try a different image
2. Ensure image has visible text
3. Check image quality (not blurry)
4. Verify image format (JPG/PNG)

### ⚠️ Test 4 Skipped: "Model Not Found"
**This is expected!** To train model:
```bash
# 1. Add CONLL data to data/custom_indian/
# 2. Train model
python -m src.training.train
```

---

## ✅ Expected Test Results (Before Training)

| Test | Expected | Reason |
|------|----------|--------|
| API Configuration | ✅ PASS | API key configured |
| OCR Extraction | ✅ PASS | Sarvam API working |
| Text Preprocessing | ✅ PASS | Cleaning functions ready |
| NER Extraction | ⚠️ SKIP | Model not trained yet |
| Complete Pipeline | ⚠️ SKIP | Model not trained yet |

**Overall: 3/5 tests pass = SUCCESS** ✅

---

## ✅ Expected Test Results (After Training)

| Test | Expected | Reason |
|------|----------|--------|
| API Configuration | ✅ PASS | API key configured |
| OCR Extraction | ✅ PASS | Sarvam API working |
| Text Preprocessing | ✅ PASS | Cleaning functions ready |
| NER Extraction | ✅ PASS | Model trained and loaded |
| Complete Pipeline | ✅ PASS | Full pipeline functional |

**Overall: 5/5 tests pass = COMPLETE** 🎉

---

## 🎬 Demo Commands Quick Reference

| Command | Purpose | Time |
|---------|---------|------|
| `python quick_test.py` | Fast API test | 30s |
| `streamlit run demo_ocr.py` | Visual demo | 2min |
| `python test_api_pipeline.py` | Full system test | 1min |
| `run_demo.bat` (Windows) | All-in-one | 3min |
| `./run_demo.sh` (Linux/Mac) | All-in-one | 3min |

---

## 📹 Video of Expected Behavior

**Command Line Test:**
```
$ python quick_test.py
============================================
  🔬 QUICK OCR API TEST
============================================

🔑 Testing API Configuration
✅ Configuration loaded successfully

📸 Testing OCR Extraction
Image: prescription1.jpg

🔄 Calling Sarvam Vision API...
   (This may take 5-10 seconds)

✅ SUCCESS! Text extracted

📝 Extracted Text (245 characters):
======================================================================
Tab Crocin 500mg
Take 1 tablet twice daily after meals
Duration: 3 days

Cap Dolo 650mg
Take 1 capsule when fever
Maximum 3 times per day
======================================================================

📊 Statistics:
   Characters: 245
   Words: 42
   Lines: 8

✅ ALL TESTS PASSED!
🎉 Your Sarvam Vision API is working correctly!
```

---

## 🎉 Success Criteria

Your system is working if:
- ✅ `quick_test.py` shows "ALL TESTS PASSED"
- ✅ `demo_ocr.py` extracts text from uploaded images
- ✅ `test_api_pipeline.py` passes 3/5 tests (before training)
- ✅ No error messages about API key
- ✅ Extracted text is visible and readable

---

## 📞 Help & Support

If tests fail:
1. Check `.env` file has correct API key
2. Verify internet connection
3. Review error messages in terminal
4. Check logs in `outputs/logs/`
5. Try with different prescription image

---

**Ready to test? Run:** `python quick_test.py` 🚀
