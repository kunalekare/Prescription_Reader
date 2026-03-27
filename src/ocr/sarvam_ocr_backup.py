"""
BACKUP - Old OCR module using Sarvam.ai API for text extraction from prescription images.
This file is a backup of the previous implementation before switching to Document Intelligence API.
"""

import requests
from pathlib import Path
from typing import Union, Optional
import time

from ..utils.config import get_ocr_config
from ..utils.logger import get_logger
from ..utils.file_utils import validate_path

logger = get_logger(__name__)

# [Old implementation - see original file for full code]
# This is just a backup marker file
