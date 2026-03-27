"""
Test script to verify Prescription Reader setup and modules.
Run this to ensure everything is installed and configured correctly.
"""

import sys
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def test_imports():
    """Test if all required modules can be imported."""
    print_header("Testing Imports")
    
    modules = [
        ("sarvamai", "Sarvam AI SDK"),
        ("torch", "PyTorch"),
        ("transformers", "HuggingFace Transformers"),
        ("streamlit", "Streamlit"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("PIL", "Pillow"),
        ("requests", "Requests"),
        ("seqeval", "Seqeval"),
    ]
    
    all_good = True
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {display_name:30s} - OK")
        except ImportError as e:
            print(f"❌ {display_name:30s} - MISSING")
            all_good = False
    
    return all_good

def test_project_modules():
    """Test if project modules can be imported."""
    print_header("Testing Project Modules")
    
    modules = [
        ("src.utils.config", "Configuration"),
        ("src.utils.logger", "Logger"),
        ("src.utils.file_utils", "File Utils"),
        ("src.ocr.sarvam_ocr", "OCR Module"),
        ("src.preprocessing.text_cleaner", "Text Cleaner"),
        ("src.inference.predict", "Inference"),
        ("src.training.train", "Training"),
        ("src.evaluation.evaluate", "Evaluation"),
        ("src.dataset.conll_loader", "Dataset Loader"),
    ]
    
    all_good = True
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {display_name:30s} - OK")
        except Exception as e:
            print(f"❌ {display_name:30s} - ERROR: {str(e)[:40]}")
            all_good = False
    
    return all_good

def test_configuration():
    """Test configuration loading."""
    print_header("Testing Configuration")
    
    try:
        from src.utils.config import get_config
        
        config = get_config()
        
        print(f"✅ Configuration loaded successfully")
        print(f"   Project root: {config.paths.project_root}")
        print(f"   Model path: {config.paths.biobert_model_path}")
        print(f"   Batch size: {config.model.batch_size}")
        print(f"   Learning rate: {config.model.learning_rate}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration failed: {str(e)}")
        return False

def test_api_key():
    """Test if API key is configured."""
    print_header("Testing API Key")
    
    try:
        from src.utils.config import get_ocr_config
        
        ocr_config = get_ocr_config()
        
        if ocr_config.api_key:
            print(f"✅ API key configured: {ocr_config.api_key[:10]}...")
            return True
        else:
            print(f"⚠️  API key not found")
            print(f"   Please add SARVAM_API_KEY to .env file")
            return False
            
    except Exception as e:
        print(f"❌ API key check failed: {str(e)}")
        print(f"   Please create .env file with SARVAM_API_KEY")
        return False

def test_directories():
    """Test if required directories exist."""
    print_header("Testing Directory Structure")
    
    try:
        from src.utils.config import get_paths
        
        paths = get_paths()
        
        dirs_to_check = [
            ("Models", paths.models_dir),
            ("Data", paths.data_dir),
            ("Outputs", paths.outputs_dir),
            ("Checkpoints", paths.checkpoint_dir),
            ("Predictions", paths.predictions_dir),
            ("Metrics", paths.metrics_dir),
            ("Logs", paths.logs_dir),
        ]
        
        all_good = True
        for name, path in dirs_to_check:
            if path.exists():
                print(f"✅ {name:20s} - {path}")
            else:
                print(f"⚠️  {name:20s} - Created: {path}")
                path.mkdir(parents=True, exist_ok=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Directory check failed: {str(e)}")
        return False

def test_label_mappings():
    """Test if label mappings exist."""
    print_header("Testing Label Mappings")
    
    try:
        from src.utils.config import get_paths
        from src.utils.file_utils import file_exists, read_json
        
        paths = get_paths()
        
        if file_exists(paths.label_map_path):
            label_map = read_json(paths.label_map_path)
            print(f"✅ Label map found: {len(label_map)} labels")
            for label, id in list(label_map.items())[:5]:
                print(f"   {label:20s} -> {id}")
            if len(label_map) > 5:
                print(f"   ... and {len(label_map) - 5} more")
            return True
        else:
            print(f"⚠️  Label map not found at {paths.label_map_path}")
            return False
            
    except Exception as e:
        print(f"❌ Label mapping check failed: {str(e)}")
        return False

def test_cuda():
    """Test CUDA availability."""
    print_header("Testing CUDA")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            print(f"✅ CUDA available")
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA version: {torch.version.cuda}")
            print(f"   Device count: {torch.cuda.device_count()}")
        else:
            print(f"ℹ️  CUDA not available - using CPU")
            print(f"   Training and inference will be slower")
        
        return True
        
    except Exception as e:
        print(f"❌ CUDA check failed: {str(e)}")
        return False

def print_summary(results):
    """Print test summary."""
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"Total tests: {total}")
    print(f"✅ Passed: {passed}")
    if failed > 0:
        print(f"❌ Failed: {failed}")
    
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if failed == 0 else '⚠️ SOME TESTS FAILED'}")
    
    if not results.get('api_key', False):
        print(f"\n⚠️  Important: Configure SARVAM_API_KEY in .env file to use OCR")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  PRESCRIPTION READER - SYSTEM CHECK")
    print("="*60)
    
    results = {}
    
    # Run tests
    results['imports'] = test_imports()
    results['project_modules'] = test_project_modules()
    results['configuration'] = test_configuration()
    results['api_key'] = test_api_key()
    results['directories'] = test_directories()
    results['label_mappings'] = test_label_mappings()
    results['cuda'] = test_cuda()
    
    # Print summary
    print_summary(results)
    
    # Exit code
    if all(results.values()):
        print("\n🎉 System is ready! You can now:")
        print("   1. Run the web interface: streamlit run app.py")
        print("   2. Train the model: python -m src.training.train")
        print("   3. Process prescriptions: python main.py <image_path>")
        sys.exit(0)
    else:
        print("\n⚠️  Please fix the issues above before proceeding")
        sys.exit(1)

if __name__ == "__main__":
    main()
