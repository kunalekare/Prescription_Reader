"""
Logging utility for Prescription Reader project.
Provides structured logging with both console and file output.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from .config import get_logging_config, get_paths


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with console and optional file output.
    
    Args:
        name: Name of the logger (usually __name__)
        log_file: Optional specific log file path
        level: Optional log level override
        
    Returns:
        Configured logger instance
    """
    log_config = get_logging_config()
    paths = get_paths()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level or log_config.log_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(log_config.log_format)
    
    # Console handler
    if log_config.console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level or log_config.log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_config.file_logging:
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = paths.logs_dir / f"prescription_reader_{timestamp}.log"
        else:
            log_file = Path(log_file)
        
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level or log_config.log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with the standard configuration.
    
    Args:
        name: Name of the logger (usually __name__)
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set it up
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


class LoggerMixin:
    """Mixin class to add logging capability to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
