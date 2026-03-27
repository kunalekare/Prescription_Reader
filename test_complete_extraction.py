"""
Complete Text Extraction Test
This script tests the full OCR pipeline with Sarvam Document Intelligence API.
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("="*70)
print("  PRESCRIPTION TEXT EXTRACTION TEST")
print("="*70)
print()

# Step 1: Check if sarvamai is installed
print("Step 1: Checking Sarvam SDK installation...")
try:
    from sarvamai import SarvamAI
    print("✅ Sarvam SDK is installed")
except ImportError:
    print("❌ Sarvam SDK not found!")
    print("\n📦 Installing now...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "sarvamai"])
        print("✅ Sarvam SDK installed successfully!")
        from sarvamai import SarvamAI
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        print("\nPlease run manually: pip install sarvamai")
        sys.exit(1)

print()

# Step 2: Check API key
print("Step 2: Checking API key configuration...")
api_key = os.getenv("SARVAM_API_KEY")
if api_key:
    print(f"✅ API key found: {api_key[:20]}...")
else:
    print("❌ API key not found!")
    print("\nPlease add to .env file:")
    print("SARVAM_API_KEY=sk_kklk9ckw_LqnGK2iUaVXQgk1dTjLufGWO")
    sys.exit(1)

print()

# Step 3: Initialize client
print("Step 3: Initializing Sarvam client...")
try:
    client = SarvamAI(api_subscription_key=api_key)
    print("✅ Client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize client: {e}")
    sys.exit(1)

print()

# Step 4: Find a test image
print("Step 4: Looking for test prescription image...")
test_image = None

prescription_dir = Path("Prescrption_Data")
if prescription_dir.exists():
    for day_folder in prescription_dir.glob("Day*"):
        images = list(day_folder.glob("*.jpg"))
        if images:
            test_image = str(images[0])
            break

if not test_image:
    print("❌ No test image found in Prescrption_Data/")
    print("\nPlease provide an image path:")
    test_image = input("Image path: ").strip()
    if not Path(test_image).exists():
        print(f"❌ Image not found: {test_image}")
        sys.exit(1)

print(f"✅ Using test image: {test_image}")
print()

# Step 5: Extract text using Document Intelligence
print("Step 5: Extracting text using Document Intelligence API...")
print("⏳ This may take 10-30 seconds...")
print()

try:
    import time
    import tempfile
    import zipfile
    
    # Create job
    print("   Creating job...")
    job = client.document_intelligence.create_job(
        language="hi-IN",
        output_format="md"
    )
    print(f"   ✅ Job created: {job.job_id}")
    
    # Upload file
    print(f"   Uploading image...")
    job.upload_file(test_image)
    print(f"   ✅ Image uploaded")
    
    # Start processing
    print(f"   Starting processing...")
    job.start()
    print(f"   ✅ Processing started")
    
    # Wait for completion
    print(f"   ⏳ Waiting for completion...")
    start_time = time.time()
    status = job.wait_until_complete()
    elapsed = time.time() - start_time
    
    print(f"   ✅ Job completed in {elapsed:.2f} seconds")
    print(f"   Status: {status.job_state}")
    
    # Get metrics
    try:
        metrics = job.get_page_metrics()
        print(f"   📊 Metrics: {metrics}")
    except:
        pass
    
    print()
    
    # Download output
    print("   Downloading results...")
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "output.zip"
        job.download_output(str(output_path))
        print(f"   ✅ Downloaded output ZIP")
        
        # Extract ZIP
        extracted_dir = Path(temp_dir) / "extracted"
        extracted_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(output_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_dir)
        
        print(f"   📂 Extracted files:")
        for f in extracted_dir.glob("*"):
            print(f"      - {f.name}")
        
        # Read text files
        text_files = list(extracted_dir.glob("*.md"))
        if not text_files:
            text_files = list(extracted_dir.glob("*.txt"))
        if not text_files:
            text_files = [f for f in extracted_dir.glob("*") if f.is_file()]
        
        if text_files:
            text_file = text_files[0]
            with open(text_file, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
            
            print()
            print("="*70)
            print("  ✅ TEXT EXTRACTION SUCCESSFUL!")
            print("="*70)
            print()
            print(f"📝 Extracted Text ({len(extracted_text)} characters):")
            print("-"*70)
            print(extracted_text)
            print("-"*70)
            print()
            
            # Save to file
            output_file = Path("outputs") / f"extracted_text_{job.job_id}.txt"
            output_file.parent.mkdir(exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            print(f"💾 Saved to: {output_file}")
            print()
            
        else:
            print("❌ No text file found in output")
    
    print("="*70)
    print("  🎉 TEXT EXTRACTION COMPLETE!")
    print("="*70)
    print()
    print("Next steps:")
    print("1. Try the web demo: streamlit run demo_ocr.py")
    print("2. Test more images with different prescriptions")
    print("3. Train NER model to extract drug names, dosages, etc.")
    print()

except Exception as e:
    print()
    print("="*70)
    print("  ❌ TEXT EXTRACTION FAILED")
    print("="*70)
    print()
    print(f"Error: {str(e)}")
    print()
    print("Troubleshooting:")
    print("1. Check API key is correct")
    print("2. Check internet connection")
    print("3. Check image file is valid (JPG/PNG)")
    print("4. Contact Sarvam support: support@sarvam.ai")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)
