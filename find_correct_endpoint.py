"""
Direct test of Sarvam API with different endpoints
"""

import requests
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SARVAM_API_KEY")

# Test different possible endpoints
ENDPOINTS = [
    "https://api.sarvam.ai/vision",
    "https://api.sarvam.ai/v1/vision",
    "https://api.sarvam.ai/v2/vision",
    "https://api.sarvam.ai/ocr",
    "https://api.sarvam.ai/v1/ocr",
]

def test_endpoint(endpoint, image_path):
    """Test a specific endpoint."""
    print(f"\n{'='*70}")
    print(f"Testing: {endpoint}")
    print(f"{'='*70}")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "api-subscription-key": API_KEY,  # Alternative auth method
    }
    
    try:
        with open(image_path, "rb") as f:
            files = {"file": (Path(image_path).name, f, "image/jpeg")}
            
            # Try with Bearer token
            print("Trying with Bearer token...")
            response = requests.post(endpoint, headers={"Authorization": f"Bearer {API_KEY}"}, files=files, timeout=30)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code == 200:
                print(f"✅ SUCCESS with endpoint: {endpoint}")
                return endpoint, response.json()
            
            # Try with api-subscription-key
            print("\nTrying with api-subscription-key...")
            with open(image_path, "rb") as f2:
                files2 = {"file": (Path(image_path).name, f2, "image/jpeg")}
                response2 = requests.post(endpoint, headers={"api-subscription-key": API_KEY}, files=files2, timeout=30)
                
                print(f"Status: {response2.status_code}")
                print(f"Response: {response2.text[:500]}")
                
                if response2.status_code == 200:
                    print(f"✅ SUCCESS with endpoint: {endpoint} (using api-subscription-key)")
                    return endpoint, response2.json()
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return None, None

def main():
    """Test all endpoints."""
    print("\n" + "="*70)
    print("  SARVAM API ENDPOINT FINDER")
    print("="*70)
    
    print(f"\nAPI Key: {API_KEY[:20]}...")
    
    # Find a test image
    prescription_dir = Path("Prescrption_Data")
    test_image = None
    
    if prescription_dir.exists():
        for day_folder in prescription_dir.glob("Day*"):
            images = list(day_folder.glob("*.jpg")) + list(day_folder.glob("*.png"))
            if images:
                test_image = images[0]
                break
    
    if not test_image:
        print("\n❌ No test images found in Prescrption_Data/")
        print("Please provide an image path manually")
        return
    
    print(f"Test Image: {test_image}")
    
    # Test each endpoint
    for endpoint in ENDPOINTS:
        working_endpoint, response = test_endpoint(endpoint, str(test_image))
        if working_endpoint:
            print(f"\n{'='*70}")
            print(f"✅ FOUND WORKING ENDPOINT!")
            print(f"{'='*70}")
            print(f"Endpoint: {working_endpoint}")
            print(f"Response structure: {list(response.keys()) if isinstance(response, dict) else type(response)}")
            print(f"Full response: {response}")
            
            print(f"\n💡 Update your config.py with:")
            print(f"   api_url: str = \"{working_endpoint}\"")
            break
    else:
        print(f"\n{'='*70}")
        print(f"❌ NO WORKING ENDPOINT FOUND")
        print(f"{'='*70}")
        print(f"\n💡 Possible issues:")
        print(f"   1. API key may be invalid")
        print(f"   2. Sarvam API structure may have changed")
        print(f"   3. Need to check Sarvam documentation")
        print(f"\n📚 Check documentation at: https://docs.sarvam.ai/")

if __name__ == "__main__":
    main()
