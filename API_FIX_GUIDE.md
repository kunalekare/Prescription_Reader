# 🔧 API ENDPOINT FIX GUIDE

## Problem
Getting 404 error: "Not Found" from Sarvam API

## Solution Steps

### Step 1: Run Endpoint Test
```bash
python test_sarvam_endpoint.py
```

This will test different Sarvam API endpoints to find the correct one.

### Step 2: Update Configuration

Once you find the working endpoint, update `src/utils/config.py`:

```python
@dataclass
class OCRConfig:
    api_key: str = field(default_factory=lambda: os.getenv("SARVAM_API_KEY", ""))
    api_url: str = "PUT_WORKING_ENDPOINT_HERE"  # Update this
    timeout: int = 30
    max_retries: int = 3
```

### Step 3: Possible Endpoints to Try

The Sarvam API might use one of these endpoints:

1. `https://api.sarvam.ai/v1/image/ocr` ← Most likely
2. `https://api.sarvam.ai/vision`
3. `https://api.sarvam.ai/v1/vision`
4. `https://api.sarvam.ai/ocr`

### Step 4: Verify API Key Format

Your API key should be used as:
```
Authorization: Bearer sk_kklk9ckw_LqnGK2iUaVXQgk1dTjLufGWO
```

## Quick Fix (Try This First)

I've already updated the endpoint to:
```
https://api.sarvam.ai/v1/image/ocr
```

**Try the demo again:**
```bash
streamlit run demo_ocr.py
```

If it still doesn't work, run:
```bash
python test_sarvam_endpoint.py
```

## Alternative: Check Sarvam Documentation

Visit: https://docs.sarvam.ai/
Look for: "Vision API" or "OCR API" section

## Contact Sarvam Support

If the endpoint test doesn't find a working URL:
- Email: support@sarvam.ai
- Tell them: "Need correct OCR/Vision API endpoint for prescription text extraction"
- Provide your API key: sk_kklk9ckw_LqnGK2iUaVXQgk1dTjLufGWO

## Manual Test (Using curl)

```bash
curl -X POST https://api.sarvam.ai/v1/image/ocr \
  -H "Authorization: Bearer sk_kklk9ckw_LqnGK2iUaVXQgk1dTjLufGWO" \
  -F "file=@your_prescription.jpg"
```

Replace endpoint URL until you find one that returns 200 OK.
