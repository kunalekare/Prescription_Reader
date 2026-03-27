"""
OCR module using Sarvam Document Intelligence API.
Extracts text from prescription images using Sarvam's Document Intelligence service.
"""

import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, Union
import tempfile
import zipfile
import json

from sarvamai import SarvamAI

from ..utils.config import get_ocr_config
from ..utils.logger import get_logger
from ..utils.file_utils import validate_path

logger = get_logger(__name__)


class OCRError(Exception):
    """Custom exception for OCR-related errors."""
    pass


class APIConnectionError(OCRError):
    """Exception for API connection issues."""
    pass


class InvalidImageError(OCRError):
    """Exception for invalid image file issues."""
    pass


def extract_text_from_image(
    image_path: Union[str, Path],
    retry: bool = True,
    language: str = "hi-IN"
) -> str:
    """
    Extract text from prescription image using Sarvam Document Intelligence API.
    
    This uses a job-based workflow:
    1. Create a document intelligence job
    2. Upload the image file
    3. Start processing
    4. Wait for completion
    5. Download and extract results
    
    Args:
        image_path: Path to prescription image
        retry: Whether to retry on failure (currently unused, kept for compatibility)
        language: Language code (default: hi-IN for Hindi/multilingual Indian)
                 Supported: hi-IN, ta-IN, te-IN, bn-IN, gu-IN, kn-IN, ml-IN, mr-IN, pa-IN, etc.
    
    Returns:
        Extracted text content as string
    
    Raises:
        InvalidImageError: If image file is invalid
        APIConnectionError: If API connection fails
        OCRError: For other OCR-related errors
    """
    try:
        # Validate image path
        image_path = validate_path(image_path, must_exist=True, must_be_file=True)
        logger.info(f"Processing image with Sarvam Document Intelligence: {image_path}")
        
        # Get OCR configuration
        config = get_ocr_config()
        
        if not config.api_key:
            raise APIConnectionError("Sarvam API key not configured. Please set SARVAM_API_KEY in .env file")
        
        # Initialize Sarvam client
        client = SarvamAI(api_subscription_key=config.api_key)
        logger.debug("Sarvam AI client initialized")
        
        # Create document intelligence job
        logger.info(f"Creating document intelligence job (language: {language})")
        job = client.document_intelligence.create_job(
            language=language,
            output_format="md"  # Use markdown format for better structure
        )
        logger.info(f"Job created: {job.job_id}")
        
        # Upload the image file
        logger.info(f"Uploading file: {image_path.name}")
        job.upload_file(str(image_path))
        logger.info("File uploaded successfully")
        
        # Start processing
        logger.info("Starting job processing...")
        job.start()
        
        # Wait for completion
        logger.info("Waiting for job completion...")
        start_time = time.time()
        
        status = job.wait_until_complete()
        elapsed = time.time() - start_time
        
        logger.info(f"Job completed in {elapsed:.2f}s with state: {status.job_state}")
        
        # Check if job failed
        if status.job_state == "failed":
            raise OCRError(f"Document intelligence job failed: {status}")
        
        # Get processing metrics
        try:
            metrics = job.get_page_metrics()
            logger.debug(f"Page metrics: {metrics}")
        except Exception as e:
            logger.warning(f"Could not retrieve page metrics: {e}")
        
        # Download output to temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.zip"
            logger.info(f"Downloading output to: {output_path}")
            job.download_output(str(output_path))
            
            # Extract ZIP file
            extracted_dir = Path(temp_dir) / "extracted"
            extracted_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(output_path, 'r') as zip_ref:
                zip_ref.extractall(extracted_dir)
            
            # Find and read the text file (try multiple formats)
            text_files = list(extracted_dir.glob("*.md"))
            if not text_files:
                text_files = list(extracted_dir.glob("*.txt"))
            if not text_files:
                # Get any text-like file
                text_files = [f for f in extracted_dir.glob("*") if f.is_file()]
            
            if not text_files:
                raise OCRError(f"No output file found in ZIP. Contents: {list(extracted_dir.glob('*'))}")
            
            # Read the first text file
            extracted_text_file = text_files[0]
            logger.info(f"Reading extracted text from: {extracted_text_file.name}")
            
            with open(extracted_text_file, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
        
        # Validate extracted text
        if not extracted_text or not extracted_text.strip():
            logger.warning("No text extracted from image")
            return ""
        
        logger.info(f"Successfully extracted {len(extracted_text)} characters")
        return extracted_text.strip()
    
    except FileNotFoundError as e:
        raise InvalidImageError(f"Image file not found: {image_path}") from e
    
    except Exception as e:
        if isinstance(e, (OCRError, APIConnectionError, InvalidImageError)):
            raise
        
        error_msg = f"Failed to extract text from {image_path}: {str(e)}"
        logger.error(error_msg)
        raise OCRError(error_msg) from e


def extract_text_with_metadata(
    image_path: Union[str, Path],
    language: str = "hi-IN"
) -> Dict[str, Any]:
    """
    Extract text with additional metadata.
    
    Args:
        image_path: Path to prescription image
        language: Language code
    
    Returns:
        Dictionary containing text and metadata
    """
    try:
        image_path = validate_path(image_path, must_exist=True, must_be_file=True)
        config = get_ocr_config()
        
        client = SarvamAI(api_subscription_key=config.api_key)
        
        job = client.document_intelligence.create_job(
            language=language,
            output_format="md"
        )
        
        job.upload_file(str(image_path))
        job.start()
        
        start_time = time.time()
        status = job.wait_until_complete()
        elapsed = time.time() - start_time
        
        # Get metrics
        try:
            metrics = job.get_page_metrics()
        except:
            metrics = None
        
        # Download and extract
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.zip"
            job.download_output(str(output_path))
            
            extracted_dir = Path(temp_dir) / "extracted"
            extracted_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(output_path, 'r') as zip_ref:
                zip_ref.extractall(extracted_dir)
            
            text_files = list(extracted_dir.glob("*.md")) or list(extracted_dir.glob("*.txt"))
            
            if text_files:
                with open(text_files[0], 'r', encoding='utf-8') as f:
                    text = f.read().strip()
            else:
                text = ""
        
        return {
            "text": text,
            "language": language,
            "job_id": job.job_id,
            "success": bool(text),
            "metadata": {
                "job_state": status.job_state,
                "metrics": metrics,
                "processing_time": elapsed
            }
        }
    
    except Exception as e:
        logger.error(f"Error extracting text with metadata: {e}")
        return {
            "text": "",
            "success": False,
            "error": str(e)
        }


def batch_extract_text(image_paths: list) -> Dict[str, str]:
    """
    Extract text from multiple images.
    
    Args:
        image_paths: List of image file paths
    
    Returns:
        Dictionary mapping image paths to extracted text
    """
    results = {}
    
    for image_path in image_paths:
        try:
            text = extract_text_from_image(image_path)
            results[str(image_path)] = text
        except Exception as e:
            logger.error(f"Failed to process {image_path}: {e}")
            results[str(image_path)] = ""
    
    return results


def validate_image_quality(image_path: Union[str, Path]) -> bool:
    """
    Perform basic validation on image quality/format.
    
    Args:
        image_path: Path to image file
        
    Returns:
        True if image appears valid, False otherwise
    """
    try:
        image_path = Path(image_path)
        
        # Check file extension
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        if image_path.suffix.lower() not in valid_extensions:
            logger.warning(f"Potentially unsupported image format: {image_path.suffix}")
            return False
        
        # Check file size (should be reasonable)
        file_size_mb = image_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 10:
            logger.warning(f"Image file very large ({file_size_mb:.1f}MB), may take longer to process")
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating image: {str(e)}")
        return False