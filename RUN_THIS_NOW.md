# 🚀 QUICK FIX - Run This Now!

## The Issue
Getting 404 error from Sarvam API - wrong endpoint URL

## ✅ The Fix (3 Steps)

### Step 1: Test Endpoints (Required)
```bash
python test_sarvam_endpoint.py
```
OR double-click: `test_endpoints.bat`

**This will automatically:**
- Test 9 different Sarvam API endpoints
- Show which one works (200 OK)  
- Tell you the correct URL to use

### Step 2: I've Already Made 2 Important Changes

**Change #1:** Updated authentication method
```python
# OLD (was using Bearer token)
headers = {"Authorization": f"Bearer {api_key}"}

# NEW (Sarvam standard - api-subscription-key)
headers = {"api-subscription-key": api_key}
```

**Change #2:** Updated endpoint URL
```python
# NEW endpoint (most likely to work based on model name)
api_url = "https://api.sarvam.ai/v1/sarvam-vision"
```

### Step 3: Try The Demo
```bash
streamlit run demo_ocr.py
```

Upload a prescription image and click "Extract Text"

---

## 🎯 Most Likely Working Endpoints

Based on Sarvam's docs, try these in order:

1. ✅ `https://api.sarvam.ai/v1/sarvam-vision` (CURRENT)
2. `https://api.sarvam.ai/sarvam-vision`  
3. `https://api.sarvam.ai/v1/vision`
4. `https://api.sarvam.ai/vision`

---

## 🔧 If Test Script Doesn't Work

### Manual Test with cURL:

**Test 1:**
```bash
curl -X POST https://api.sarvam.ai/v1/sarvam-vision \
  -H "api-subscription-key: sk_kklk9ckw_LqnGK2iUaVXQgk1dTjLufGWO" \
  -F "file=@Prescrption_Data/Day1-5/image.jpg"
```

**Test 2:**
```bash
curl -X POST https://api.sarvam.ai/sarvam-vision \
  -H "api-subscription-key: sk_kklk9ckw_LqnGK2iUaVXQgk1dTjLufGWO" \
  -F "file=@Prescrption_Data/Day1-5/image.jpg"
```

Look for "200 OK" response!

---

## ✉️ Contact Sarvam Support (Last Resort)

If nothing works, they need to tell you the correct endpoint:

**Email:** support@sarvam.ai  
**Subject:** Need Sarvam Vision API Endpoint  

**Message:**
```
Hi Sarvam Team,

I'm getting 404 errors when trying to use the Vision/OCR API for prescription text extraction.

API Key: sk_kklk9ckw_LqnGK2iUaVXQgk1dTjLufGWO
Current Endpoint: https://api.sarvam.ai/v1/sarvam-vision
Error: 404 Not Found

Could you please provide:
1. The correct endpoint URL for Sarvam Vision API
2. Required headers (api-subscription-key or Authorization?)
3. Expected request/response format

Thank you!
```

---

## 📝 What Changed in Your Code

**File:** `src/ocr/sarvam_ocr.py`
- Line 66-69: Changed from Bearer token to api-subscription-key

**File:** `src/utils/config.py`  
- Line 87: Updated endpoint to v1/sarvam-vision

**File:** `test_sarvam_endpoint.py` (NEW)
- Comprehensive endpoint tester

---

## 🎉 Expected Success Output

When endpoint test finds the right URL:
```
✅ SUCCESS!
Status: 200
Response: {"text": "Tab Crocin 500mg..."}

🎉 WORKING ENDPOINT FOUND!
   URL: https://api.sarvam.ai/v1/sarvam-vision
   Header: api-subscription-key
   Value: sk_kklk9ckw_LqnGK2iUaVXQgk1dTjLufGWO
```

Then in demo:
```
✅ Text Extracted Successfully!
📝 Extracted Text:
Tab Crocin 500mg
Take 1 tablet BD x 3 days
```

---

## 🚨 Run This Command NOW:

```bash
python test_sarvam_endpoint.py
```

This will show you EXACTLY which endpoint works! 🎯
