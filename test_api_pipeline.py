"""
Test script for Sarvam Vision API and complete NER pipeline.
Tests OCR extraction and entity recognition with real API.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_api_connection():
    """Test Sarvam Vision API connection."""
    print("\n" + "="*70)
    print("  TEST 1: Sarvam Vision API Connection")
    print("="*70 + "\n")
    
    try:
        from src.utils.config import get_ocr_config
        
        config = get_ocr_config()
        
        print(f"✅ Configuration loaded")
        print(f"   API URL: {config.api_url}")
        print(f"   API Key: {config.api_key[:15]}..." if config.api_key else "   ❌ No API key found")
        print(f"   Timeout: {config.timeout}s")
        print(f"   Max Retries: {config.max_retries}")
        
        if not config.api_key:
            print(f"\n❌ FAILED: No API key configured")
            return False
        
        print(f"\n✅ PASSED: API configuration valid")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False


def test_ocr_with_sample():
    """Test OCR extraction with a sample image."""
    print("\n" + "="*70)
    print("  TEST 2: OCR Text Extraction (Sample Image)")
    print("="*70 + "\n")
    
    try:
        from src.ocr.sarvam_ocr import extract_text_from_image
        
        # Check for sample images
        prescription_dir = Path("Prescrption_Data")
        
        if not prescription_dir.exists():
            print(f"⚠️  No sample images found in {prescription_dir}")
            print(f"   Skipping OCR test")
            return None
        
        # Find first image
        sample_images = []
        for day_folder in prescription_dir.glob("Day*"):
            images = list(day_folder.glob("*.jpg")) + list(day_folder.glob("*.png"))
            if images:
                sample_images.extend(images[:2])  # Take first 2 from each folder
                if len(sample_images) >= 2:
                    break
        
        if not sample_images:
            print(f"⚠️  No JPG/PNG images found")
            print(f"   Skipping OCR test")
            return None
        
        # Test with first image
        test_image = sample_images[0]
        print(f"📸 Testing with: {test_image.name}")
        print(f"   Location: {test_image.parent.name}/{test_image.name}")
        print(f"\n🔄 Extracting text...")
        
        extracted_text = extract_text_from_image(str(test_image))
        
        if extracted_text:
            print(f"\n✅ PASSED: Text extracted successfully!")
            print(f"\n📝 Extracted Text ({len(extracted_text)} characters):")
            print(f"{'='*70}")
            print(extracted_text[:500] + ("..." if len(extracted_text) > 500 else ""))
            print(f"{'='*70}")
            return extracted_text
        else:
            print(f"\n⚠️  WARNING: No text extracted (empty response)")
            return ""
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        print(f"\nFull error:")
        traceback.print_exc()
        return False


def test_text_cleaning(raw_text):
    """Test text preprocessing."""
    print("\n" + "="*70)
    print("  TEST 3: Text Preprocessing")
    print("="*70 + "\n")
    
    if raw_text is None:
        print(f"⚠️  Skipped (no text from OCR)")
        return None
    
    if raw_text is False:
        print(f"❌ Skipped (OCR failed)")
        return False
    
    try:
        from src.preprocessing.text_cleaner import clean_text
        
        print(f"🔄 Cleaning text...")
        cleaned_text = clean_text(raw_text)
        
        print(f"\n✅ PASSED: Text cleaned successfully!")
        print(f"\n📝 Cleaned Text ({len(cleaned_text)} characters):")
        print(f"{'='*70}")
        print(cleaned_text[:500] + ("..." if len(cleaned_text) > 500 else ""))
        print(f"{'='*70}")
        
        return cleaned_text
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False


def test_ner_inference(cleaned_text):
    """Test NER entity extraction."""
    print("\n" + "="*70)
    print("  TEST 4: NER Entity Extraction")
    print("="*70 + "\n")
    
    if cleaned_text is None:
        print(f"⚠️  Skipped (no cleaned text)")
        return None
    
    if cleaned_text is False:
        print(f"❌ Skipped (preprocessing failed)")
        return False
    
    try:
        from src.inference.predict import get_predictor
        
        # Check if model exists
        from src.utils.config import get_paths
        paths = get_paths()
        
        if not paths.biobert_model_path.exists():
            print(f"⚠️  Model not found at: {paths.biobert_model_path}")
            print(f"   You need to train the model first:")
            print(f"   python -m src.training.train")
            return None
        
        print(f"🔄 Loading NER model...")
        predictor = get_predictor()
        
        print(f"🔄 Predicting entities...")
        token_predictions = predictor.predict_entities(cleaned_text)
        
        print(f"🔄 Extracting structured entities...")
        entities = predictor.extract_entities(token_predictions)
        
        print(f"\n✅ PASSED: Entities extracted successfully!")
        
        if entities:
            print(f"\n🎯 Extracted Entities:")
            print(f"{'='*70}")
            for entity_type, values in entities.items():
                if values:
                    print(f"\n{entity_type}:")
                    for value in values:
                        print(f"  • {value}")
            print(f"{'='*70}")
        else:
            print(f"\n⚠️  No entities found in the text")
        
        return entities
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        print(f"\nFull error:")
        traceback.print_exc()
        return False


def test_complete_pipeline():
    """Test complete end-to-end pipeline."""
    print("\n" + "="*70)
    print("  TEST 5: Complete End-to-End Pipeline")
    print("="*70 + "\n")
    
    try:
        from src.inference.predict import process_prescription
        
        # Find sample image
        prescription_dir = Path("Prescrption_Data")
        
        if not prescription_dir.exists():
            print(f"⚠️  No sample images found")
            return None
        
        # Find first image
        for day_folder in prescription_dir.glob("Day*"):
            images = list(day_folder.glob("*.jpg")) + list(day_folder.glob("*.png"))
            if images:
                test_image = images[0]
                break
        else:
            print(f"⚠️  No images found")
            return None
        
        print(f"📸 Processing: {test_image.name}")
        print(f"\n🔄 Running complete pipeline...")
        
        result = process_prescription(str(test_image), return_tokens=False)
        
        if result.get("success", True):
            print(f"\n✅ PASSED: Pipeline completed successfully!")
            
            print(f"\n📊 Results:")
            print(f"{'='*70}")
            print(f"\n📝 Raw Text: {result.get('raw_text', '')[:200]}...")
            print(f"\n🧹 Cleaned Text: {result.get('cleaned_text', '')[:200]}...")
            
            entities = result.get('entities', {})
            if entities:
                print(f"\n🎯 Entities:")
                for entity_type, values in entities.items():
                    if values:
                        print(f"   {entity_type}: {', '.join(values)}")
            
            print(f"{'='*70}")
            return True
        else:
            print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  PRESCRIPTION READER - API & PIPELINE TEST")
    print("  Testing Sarvam Vision API + NER Model")
    print("="*70)
    
    # Test 1: API Configuration
    test1_result = test_api_connection()
    
    if not test1_result:
        print("\n⚠️  Cannot proceed without valid API configuration")
        print("   Please ensure .env file has SARVAM_API_KEY set")
        return
    
    # Test 2: OCR Extraction
    raw_text = test_ocr_with_sample()
    
    # Test 3: Text Cleaning
    cleaned_text = test_text_cleaning(raw_text)
    
    # Test 4: NER Inference
    entities = test_ner_inference(cleaned_text)
    
    # Test 5: Complete Pipeline
    pipeline_result = test_complete_pipeline()
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    tests = {
        "API Configuration": test1_result,
        "OCR Extraction": raw_text not in [None, False],
        "Text Cleaning": cleaned_text not in [None, False],
        "NER Extraction": entities not in [None, False],
        "Complete Pipeline": pipeline_result
    }
    
    passed = sum(1 for v in tests.values() if v is True)
    total = len(tests)
    
    print(f"\n📊 Results:")
    for test_name, result in tests.items():
        status = "✅ PASSED" if result is True else "⚠️  SKIPPED" if result is None else "❌ FAILED"
        print(f"   {test_name:25s}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n🎉 SUCCESS! All systems operational!")
        print(f"\n📱 Next Steps:")
        print(f"   1. Train model: python -m src.training.train")
        print(f"   2. Run web UI: streamlit run app.py")
        print(f"   3. Process prescription: python main.py <image_path>")
    else:
        print(f"\n⚠️  Some tests need attention")
        if entities is None:
            print(f"\n💡 To train the model:")
            print(f"   1. Add CONLL data to data/custom_indian/")
            print(f"   2. Run: python -m src.training.train")


if __name__ == "__main__":
    main()
