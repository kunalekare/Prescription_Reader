"""
Simple API endpoint test - Check Sarvam Vision API
Run this to find the correct endpoint and authentication method
"""

import requests
import os
from pathlib import Path

# Your API key
API_KEY = "sk_kklk9ckw_LqnGK2iUaVXQgk1dTjLufGWO"

# Find a test image
def find_test_image():
    prescription_dir = Path("Prescrption_Data")
    if prescription_dir.exists():
        for day_folder in prescription_dir.glob("Day*"):
            images = list(day_folder.glob("*.jpg"))[:1]
            if images:
                return str(images[0])
    return None

print("="*70)
print("  TESTING SARVAM API ENDPOINTS")
print("="*70)

test_image = find_test_image()
if not test_image:
    print("\n❌ No test image found. Please add images to Prescrption_Data/")
    exit(1)

print(f"\nTest image: {test_image}")
print(f"API Key: {API_KEY[:20]}...\n")

# Test different endpoints and methods based on Sarvam API patterns
tests = [
    # Vision endpoints with Authorization header
    ("https://api.sarvam.ai/v1/sarvam-vision", "api-subscription-key", "Direct"),
    ("https://api.sarvam.ai/sarvam-vision", "api-subscription-key", "Direct"),
    ("https://api.sarvam.ai/vision", "api-subscription-key", "Direct"),
    ("https://api.sarvam.ai/v1/vision", "api-subscription-key", "Direct"),
    
    # OCR endpoints
    ("https://api.sarvam.ai/v1/image/ocr", "api-subscription-key", "Direct"),
    ("https://api.sarvam.ai/v1/ocr", "api-subscription-key", "Direct"),
    ("https://api.sarvam.ai/ocr", "api-subscription-key", "Direct"),
    
    # Try with Authorization header (Bearer)
    ("https://api.sarvam.ai/v1/sarvam-vision", "Authorization", "Bearer"),
    ("https://api.sarvam.ai/vision", "Authorization", "Bearer"),
]

for endpoint, header_name, auth_type in tests:
    print(f"\nTrying: {endpoint}")
    print(f"Auth: {header_name} ({auth_type})")
    
    try:
        with open(test_image, "rb") as f:
            files = {"file": ("prescription.jpg", f, "image/jpeg")}
            
            if auth_type == "Bearer":
                headers = {header_name: f"Bearer {API_KEY}"}
            else:
                headers = {header_name: API_KEY}
            
            response = requests.post(endpoint, headers=headers, files=files, timeout=30)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ SUCCESS!")
                print(f"Response: {response.text[:500]}")
                print(f"\n🎉 WORKING ENDPOINT FOUND!")
                print(f"   URL: {endpoint}")
                print(f"   Header: {header_name}")
                print(f"   Value: {auth_type} {API_KEY if auth_type == 'Direct' else 'Bearer ' + API_KEY}")
                print(f"\n✏️  UPDATE src/utils/config.py with:")
                print(f'   api_url: str = "{endpoint}"')
                break
            else:
                print(f"❌ Failed - Response: {response.text[:150]}")
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")

print("\n" + "="*70)
