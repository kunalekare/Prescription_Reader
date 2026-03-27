"""
Quick API Test Script - Command Line
Test Sarvam OCR API directly from terminal
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def test_api_config():
    """Test API configuration."""
    print_header("🔑 Testing API Configuration")
    
    try:
        from src.utils.config import get_ocr_config
        
        config = get_ocr_config()
        
        print(f"✅ Configuration loaded successfully")
        print(f"   API URL: {config.api_url}")
        print(f"   API Key: {config.api_key[:20]}..." if config.api_key else "   ❌ No API key")
        print(f"   Timeout: {config.timeout}s")
        print(f"   Max Retries: {config.max_retries}")
        
        if not config.api_key:
            print(f"\n❌ ERROR: No API key found!")
            print(f"   Please add SARVAM_API_KEY to .env file")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


def find_sample_image():
    """Find a sample image to test."""
    prescription_dir = Path("Prescrption_Data")
    
    if not prescription_dir.exists():
        return None
    
    # Find first image
    for day_folder in prescription_dir.glob("Day*"):
        images = list(day_folder.glob("*.jpg")) + list(day_folder.glob("*.png"))
        if images:
            return images[0]
    
    return None


def test_ocr_extraction(image_path):
    """Test OCR extraction."""
    print_header(f"📸 Testing OCR Extraction")
    
    print(f"Image: {image_path.name}")
    print(f"Location: {image_path.parent.name}/{image_path.name}")
    
    try:
        from src.ocr.sarvam_ocr import extract_text_from_image
        
        print(f"\n🔄 Calling Sarvam Vision API...")
        print(f"   (This may take 5-10 seconds)")
        
        # Extract text
        extracted_text = extract_text_from_image(str(image_path))
        
        if extracted_text:
            print(f"\n✅ SUCCESS! Text extracted")
            print(f"\n📝 Extracted Text ({len(extracted_text)} characters):")
            print(f"{'='*70}")
            print(extracted_text)
            print(f"{'='*70}")
            
            # Statistics
            words = extracted_text.split()
            lines = extracted_text.split('\n')
            
            print(f"\n📊 Statistics:")
            print(f"   Characters: {len(extracted_text)}")
            print(f"   Words: {len(words)}")
            print(f"   Lines: {len(lines)}")
            
            return True
        else:
            print(f"\n⚠️  WARNING: No text extracted (empty response)")
            print(f"   This might happen if:")
            print(f"   - Image has no text")
            print(f"   - Image quality is too low")
            print(f"   - Image is too blurry")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        
        import traceback
        print(f"\n🔍 Full Error Details:")
        print(f"{'='*70}")
        traceback.print_exc()
        print(f"{'='*70}")
        
        return False


def main():
    """Run OCR test."""
    print("\n" + "="*70)
    print("  🔬 QUICK OCR API TEST")
    print("  Testing Sarvam Vision API")
    print("="*70)
    
    # Step 1: Test config
    if not test_api_config():
        print(f"\n⚠️  Cannot proceed without valid API configuration")
        return
    
    # Step 2: Find sample image
    print_header("🔍 Finding Sample Image")
    
    sample_image = find_sample_image()
    
    if not sample_image:
        print(f"❌ No sample images found in Prescrption_Data/")
        print(f"\n💡 To test with your own image:")
        print(f"   python -c \"from src.ocr.sarvam_ocr import extract_text_from_image; print(extract_text_from_image('your_image.jpg'))\"")
        return
    
    print(f"✅ Found sample image: {sample_image.name}")
    
    # Step 3: Test OCR
    success = test_ocr_extraction(sample_image)
    
    # Summary
    print_header("📊 Test Summary")
    
    if success:
        print(f"✅ ALL TESTS PASSED!")
        print(f"\n🎉 Your Sarvam Vision API is working correctly!")
        print(f"\n📱 Next Steps:")
        print(f"   1. Run web interface: streamlit run demo_ocr.py")
        print(f"   2. Or full app: streamlit run app.py")
        print(f"   3. Process any image: python main.py <image_path>")
    else:
        print(f"❌ TEST FAILED")
        print(f"\n🔍 Troubleshooting:")
        print(f"   1. Check API key in .env file")
        print(f"   2. Verify image is clear and has text")
        print(f"   3. Try a different image")
        print(f"   4. Check internet connection")


if __name__ == "__main__":
    main()
