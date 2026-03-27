"""
Prescription Reader - Main Entry Point
Medical Information Extraction using OCR + NER
"""

from src.inference.predict import process_prescription
from src.utils.logger import get_logger
from pathlib import Path

logger = get_logger(__name__)


def main():
    """Main function for command-line usage."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <prescription_image_path>")
        print("\nExample:")
        print("  python main.py sample_prescription.jpg")
        print("\nOr run the web interface:")
        print("  streamlit run app.py")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"Error: File not found: {image_path}")
        sys.exit(1)
    
    logger.info(f"Processing prescription: {image_path}")
    print(f"\n{'='*60}")
    print(f"Processing: {image_path}")
    print(f"{'='*60}\n")
    
    # Process prescription
    result = process_prescription(image_path, return_tokens=False)
    
    # Display results
    if result.get("success", True):
        print("✅ SUCCESS!\n")
        
        print("📝 Extracted Text:")
        print("-" * 60)
        print(result.get("cleaned_text", ""))
        print()
        
        print("🎯 Extracted Entities:")
        print("-" * 60)
        
        entities = result.get("entities", {})
        if entities:
            for entity_type, values in entities.items():
                if values:
                    print(f"{entity_type:20s}: {', '.join(values)}")
        else:
            print("No entities found.")
        
        print(f"\n{'='*60}\n")
    else:
        print("❌ FAILED!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        print(f"Type: {result.get('error_type', 'Unknown')}")


if __name__ == "__main__":
    main()
