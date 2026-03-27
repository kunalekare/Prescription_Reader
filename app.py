"""
Streamlit Web Interface for Prescription Reader
Professional UI for prescription OCR and NER entity extraction
"""

import streamlit as st
import json
from pathlib import Path
import pandas as pd
from PIL import Image
import time

from src.inference.predict import process_prescription, PrescriptionPredictor, get_predictor
from src.utils.logger import get_logger
from src.utils.config import get_paths

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Prescription Reader - Medical NER",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        padding-bottom: 2rem;
    }
    .entity-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .entity-FORM {
        background-color: #e3f2fd;
        border-color: #1976d2;
    }
    .entity-DRUG {
        background-color: #f3e5f5;
        border-color: #7b1fa2;
    }
    .entity-DOSAGE {
        background-color: #e8f5e9;
        border-color: #388e3c;
    }
    .entity-FREQUENCY {
        background-color: #fff3e0;
        border-color: #f57c00;
    }
    .entity-DURATION {
        background-color: #fce4ec;
        border-color: #c2185b;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 4px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def display_header():
    """Display application header."""
    st.markdown('<div class="main-header">💊 Prescription Reader</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">AI-Powered Medical Information Extraction using OCR + NER</div>',
        unsafe_allow_html=True
    )


def display_sidebar():
    """Display sidebar with information and settings."""
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This application extracts structured medical information from prescription images using:
        
        - **OCR**: Sarvam.ai API for text extraction
        - **NER**: Fine-tuned BioBERT model
        - **Entities**: FORM, DRUG, DOSAGE, FREQUENCY, DURATION
        """)
        
        st.header("📋 Instructions")
        st.markdown("""
        1. Upload a prescription image (JPG, PNG)
        2. Wait for OCR and NER processing
        3. View extracted entities
        4. Download results as JSON
        """)
        
        st.header("🎨 Entity Types")
        entity_info = {
            "FORM": "Tablet, Capsule, Syrup",
            "DRUG_BRAND": "Brand name (e.g., Crocin)",
            "DRUG_GENERIC": "Generic name (e.g., Paracetamol)",
            "DOSAGE": "Amount (e.g., 500mg)",
            "FREQUENCY": "BD, TDS, OD, etc.",
            "DURATION": "5 days, 1 week, etc."
        }
        
        for entity, description in entity_info.items():
            st.markdown(f"**{entity}**: {description}")
        
        st.markdown("---")
        st.markdown("**Version**: 1.0.0")
        st.markdown("**Model**: BioBERT (fine-tuned)")


def display_entity_card(entity_type: str, values: list):
    """Display entity in a styled card."""
    entity_class = entity_type.split('_')[0] if '_' in entity_type else entity_type
    
    values_html = ", ".join([f"<strong>{v}</strong>" for v in values])
    
    card_html = f"""
    <div class="entity-box entity-{entity_class}">
        <div style="font-weight: bold; margin-bottom: 0.5rem;">{entity_type}</div>
        <div>{values_html}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def process_uploaded_file(uploaded_file):
    """Process uploaded prescription image."""
    try:
        # Save uploaded file temporarily
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        
        temp_path = temp_dir / uploaded_file.name
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Display image
        st.subheader("📸 Uploaded Prescription")
        image = Image.open(temp_path)
        st.image(image, use_column_width=True)
        
        # Process prescription
        st.subheader("🔄 Processing...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: OCR
        status_text.text("Step 1/3: Extracting text with OCR...")
        progress_bar.progress(33)
        time.sleep(0.5)
        
        # Step 2: Cleaning
        status_text.text("Step 2/3: Cleaning and preprocessing text...")
        progress_bar.progress(66)
        time.sleep(0.5)
        
        # Step 3: NER
        status_text.text("Step 3/3: Extracting entities with BioBERT...")
        progress_bar.progress(100)
        
        # Actually process
        result = process_prescription(str(temp_path), return_tokens=False)
        
        # Clear progress
        progress_bar.empty()
        status_text.empty()
        
        # Clean up
        temp_path.unlink()
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return {"success": False, "error": str(e)}


def display_results(result: dict):
    """Display extraction results."""
    if not result.get("success", True):
        # Display error
        error_html = f"""
        <div class="error-box">
            <strong>❌ Error:</strong> {result.get('error', 'Unknown error')}
            <br>
            <strong>Type:</strong> {result.get('error_type', 'Unknown')}
        </div>
        """
        st.markdown(error_html, unsafe_allow_html=True)
        return
    
    # Success
    st.markdown('<div class="success-box">✅ <strong>Successfully processed prescription!</strong></div>',
                unsafe_allow_html=True)
    
    # Display extracted text
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Extracted Text")
        with st.expander("Raw OCR Text", expanded=False):
            st.text(result.get("raw_text", ""))
        
        with st.expander("Cleaned Text", expanded=True):
            st.text(result.get("cleaned_text", ""))
    
    with col2:
        st.subheader("🎯 Extracted Entities")
        
        entities = result.get("entities", {})
        
        if not entities:
            st.warning("No entities found in the prescription.")
        else:
            for entity_type, values in entities.items():
                if values:
                    display_entity_card(entity_type, values)
            
            # Create DataFrame for table view
            st.subheader("📊 Entity Table")
            entity_data = []
            for entity_type, values in entities.items():
                for value in values:
                    entity_data.append({"Entity Type": entity_type, "Value": value})
            
            if entity_data:
                df = pd.DataFrame(entity_data)
                st.dataframe(df, use_container_width=True)
    
    # Download results
    st.subheader("💾 Download Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # JSON download
        json_str = json.dumps(result, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Download as JSON",
            data=json_str,
            file_name="prescription_results.json",
            mime="application/json"
        )
    
    with col2:
        # CSV download
        if entities:
            entity_data = []
            for entity_type, values in entities.items():
                for value in values:
                    entity_data.append({"Entity_Type": entity_type, "Value": value})
            
            df = pd.DataFrame(entity_data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="prescription_results.csv",
                mime="text/csv"
            )


def main():
    """Main application."""
    display_header()
    display_sidebar()
    
    st.markdown("---")
    
    # File uploader
    st.subheader("📤 Upload Prescription Image")
    
    uploaded_file = st.file_uploader(
        "Choose a prescription image...",
        type=["jpg", "jpeg", "png", "bmp"],
        help="Upload a clear image of the prescription"
    )
    
    if uploaded_file is not None:
        with st.spinner("Processing prescription..."):
            result = process_uploaded_file(uploaded_file)
            display_results(result)
    else:
        # Display sample
        st.info("👆 Please upload a prescription image to get started")
        
        # Example section
        with st.expander("📖 Example Output"):
            st.markdown("""
            **Input**: "Tab Crocin 500mg BD x 3 days"
            
            **Extracted Entities**:
            - **FORM**: Tab
            - **DRUG_BRAND**: Crocin
            - **DOSAGE**: 500mg
            - **FREQUENCY**: BD
            - **DURATION**: 3 days
            """)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Application error: {str(e)}", exc_info=True)
