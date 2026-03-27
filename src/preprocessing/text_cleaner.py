"""
Text preprocessing and cleaning module for prescription text.
Handles normalization, abbreviation expansion, and format standardization.
"""

import re
from typing import Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


class TextCleaningError(Exception):
    """Custom exception for text cleaning errors."""
    pass


def clean_text(text: Optional[str], strict: bool = False) -> str:
    """
    Clean and normalize prescription text.
    
    Args:
        text: Raw text to clean
        strict: If True, raise error on None/empty text. If False, return empty string.
        
    Returns:
        Cleaned and normalized text
        
    Raises:
        TextCleaningError: If text is None/empty and strict is True
    """
    try:
        # Handle None or empty text
        if not text:
            if strict:
                raise TextCleaningError("Cannot clean None or empty text")
            logger.warning("Received empty text for cleaning")
            return ""
        
        logger.debug(f"Cleaning text of length {len(text)}")
        
        # Convert to string if not already
        text = str(text)
        
        # Replace newlines with spaces
        text = text.replace("\n", " ").replace("\r", " ")
        
        # Normalize multiple spaces
        text = re.sub(r"\s+", " ", text)
        
        # Standardize dosage formats
        text = re.sub(r"(\d+)\s*mg", r"\1mg", text, flags=re.IGNORECASE)
        text = re.sub(r"(\d+)\s*ml", r"\1ml", text, flags=re.IGNORECASE)
        text = re.sub(r"(\d+)\s*g", r"\1g", text, flags=re.IGNORECASE)
        text = re.sub(r"(\d+)\s*mcg", r"\1mcg", text, flags=re.IGNORECASE)
        
        # Normalize frequency abbreviations (optional - keep original for NER)
        # text = text.replace("O.D.", "OD").replace("o.d.", "OD")
        # text = text.replace("B.D.", "BD").replace("b.d.", "BD")
        # text = text.replace("T.D.S.", "TDS").replace("t.d.s.", "TDS")
        
        # Remove extra punctuation spacing
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        logger.debug(f"Cleaned text to length {len(text)}")
        return text
        
    except Exception as e:
        if isinstance(e, TextCleaningError):
            raise
        logger.error(f"Error during text cleaning: {str(e)}")
        raise TextCleaningError(f"Failed to clean text: {str(e)}") from e


def normalize_prescription_text(text: str) -> str:
    """
    Advanced normalization for Indian prescription patterns.
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    try:
        # Handle common OCR errors
        text = text.replace("0D", "OD")  # Zero vs O confusion
        text = text.replace("l", "1").replace("I", "1")  # Letter vs number
        
        # Normalize common prescription terms
        replacements = {
            "tab.": "Tab",
            "cap.": "Cap",
            "syp.": "Syrup",
            "inj.": "Injection",
        }
        
        for old, new in replacements.items():
            text = re.sub(re.escape(old), new, text, flags=re.IGNORECASE)
        
        return text
        
    except Exception as e:
        logger.warning(f"Error in advanced normalization: {str(e)}")
        return text  # Return original if normalization fails


def remove_special_characters(text: str, keep_chars: str = " .,;:-") -> str:
    """
    Remove special characters while preserving specific ones.
    
    Args:
        text: Text to process
        keep_chars: Characters to preserve
        
    Returns:
        Text with special characters removed
    """
    pattern = f"[^a-zA-Z0-9{re.escape(keep_chars)}]"
    return re.sub(pattern, "", text)


def extract_numeric_values(text: str) -> list:
    """
    Extract all numeric values from text (useful for dosage extraction).
    
    Args:
        text: Text to extract from
        
    Returns:
        List of numeric strings found
    """
    return re.findall(r'\d+(?:\.\d+)?', text)