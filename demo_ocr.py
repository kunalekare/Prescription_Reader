"""
Simple Demo Frontend - Test Sarvam OCR API
Minimal interface to verify API is working
"""

import streamlit as st
import sys
from pathlib import Path
from PIL import Image
import time
import json

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Page config
st.set_page_config(
    page_title="OCR Demo - Sarvam API Test",
    page_icon="🔬",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
        color: #1f77b4;
    }
    .success-box {
        padding: 20px;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        border-radius: 5px;
        margin: 10px 0;
    }
    .error-box {
        padding: 20px;
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        border-radius: 5px;
        margin: 10px 0;
    }
    .info-box {
        padding: 20px;
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="big-font">🔬 OCR Demo - Sarvam API Test</p>', unsafe_allow_html=True)
st.markdown("---")

# Check API configuration
try:
    from src.utils.config import get_ocr_config
    config = get_ocr_config()
    
    if config.api_key:
        st.markdown(f"""
        <div class="success-box">
            ✅ <strong>API Key Configured</strong><br>
            Key: {config.api_key[:20]}...
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="error-box">
            ❌ <strong>API Key Not Found</strong><br>
            Please add SARVAM_API_KEY to .env file
        </div>
        """, unsafe_allow_html=True)
        st.stop()
except Exception as e:
    st.error(f"Configuration Error: {str(e)}")
    st.stop()

# Instructions
st.markdown("""
<div class="info-box">
    <strong>📋 Instructions:</strong>
    <ol>
        <li>Upload a prescription image (JPG, PNG)</li>
        <li>Click "Extract Text" button</li>
        <li>View extracted text from Sarvam API</li>
    </ol>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# File uploader
uploaded_file = st.file_uploader(
    "Choose a prescription image",
    type=["jpg", "jpeg", "png"],
    help="Upload a clear image of a prescription"
)

if uploaded_file is not None:
    # Display image
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📸 Uploaded Image")
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)
        
        # Image info
        st.caption(f"Filename: {uploaded_file.name}")
        st.caption(f"Size: {uploaded_file.size / 1024:.1f} KB")
        st.caption(f"Dimensions: {image.size[0]} x {image.size[1]}")
    
    with col2:
        st.subheader("📝 Extracted Text")
        
        # Extract button
        if st.button("🚀 Extract Text", type="primary", use_container_width=True):
            # Save uploaded file temporarily
            temp_dir = Path("temp_uploads")
            temp_dir.mkdir(exist_ok=True)
            temp_path = temp_dir / uploaded_file.name
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Show progress
            with st.spinner("Calling Sarvam Vision API..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Import OCR function
                    from src.ocr.sarvam_ocr import extract_text_from_image
                    
                    # Update progress
                    status_text.text("Connecting to API...")
                    progress_bar.progress(25)
                    time.sleep(0.5)
                    
                    status_text.text("Sending image...")
                    progress_bar.progress(50)
                    
                    # Call API
                    extracted_text = extract_text_from_image(str(temp_path))
                    
                    status_text.text("Processing response...")
                    progress_bar.progress(75)
                    time.sleep(0.3)
                    
                    progress_bar.progress(100)
                    status_text.text("Complete!")
                    time.sleep(0.5)
                    
                    # Clear progress
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Display results
                    if extracted_text:
                        st.markdown(f"""
                        <div class="success-box">
                            ✅ <strong>Text Extracted Successfully!</strong><br>
                            Characters: {len(extracted_text)}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show extracted text
                        st.text_area(
                            "Extracted Text:",
                            extracted_text,
                            height=300,
                            key="extracted_text"
                        )
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Text",
                            data=extracted_text,
                            file_name=f"extracted_{uploaded_file.name}.txt",
                            mime="text/plain"
                        )
                        
                        # Show JSON format
                        with st.expander("📊 View as JSON"):
                            result_json = {
                                "filename": uploaded_file.name,
                                "text": extracted_text,
                                "char_count": len(extracted_text),
                                "word_count": len(extracted_text.split())
                            }
                            st.json(result_json)
                            
                            st.download_button(
                                label="📥 Download JSON",
                                data=json.dumps(result_json, indent=2),
                                file_name=f"extracted_{uploaded_file.name}.json",
                                mime="application/json"
                            )
                    else:
                        st.markdown("""
                        <div class="error-box">
                            ⚠️ <strong>No Text Extracted</strong><br>
                            The API returned an empty response. This might happen if:
                            <ul>
                                <li>The image has no text</li>
                                <li>The image quality is too low</li>
                                <li>The image is too blurry</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Clean up
                    temp_path.unlink()
                    
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.markdown(f"""
                    <div class="error-box">
                        ❌ <strong>Error Occurred</strong><br>
                        {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show detailed error
                    with st.expander("🔍 View Error Details"):
                        import traceback
                        st.code(traceback.format_exc())
                    
                    # Clean up
                    if temp_path.exists():
                        temp_path.unlink()

# Sample images section
st.markdown("---")
st.subheader("📂 Or Try Sample Images")

# Check for sample images
prescription_dir = Path("Prescrption_Data")
if prescription_dir.exists():
    sample_images = []
    for day_folder in prescription_dir.glob("Day*"):
        images = list(day_folder.glob("*.jpg"))[:3] + list(day_folder.glob("*.png"))[:3]
        sample_images.extend(images[:3])
        if len(sample_images) >= 6:
            break
    
    if sample_images:
        st.info(f"Found {len(sample_images)} sample images in Prescrption_Data/")
        
        cols = st.columns(3)
        for idx, img_path in enumerate(sample_images[:6]):
            with cols[idx % 3]:
                try:
                    img = Image.open(img_path)
                    st.image(img, use_column_width=True)
                    st.caption(f"{img_path.parent.name}/{img_path.name}")
                    
                    if st.button(f"Use This", key=f"sample_{idx}"):
                        st.info("👆 Please use the file uploader above to test this image")
                except Exception as e:
                    st.error(f"Error loading image: {str(e)}")
    else:
        st.warning("No sample images found in Prescrption_Data/")
else:
    st.warning("Prescrption_Data/ folder not found")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <small>
    🔬 OCR Demo using Sarvam Vision API<br>
    Supports multilingual text extraction (English, Hindi, Tamil, Telugu, Bengali, etc.)
    </small>
</div>
""", unsafe_allow_html=True)
