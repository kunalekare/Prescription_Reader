"""
File utility functions for Prescription Reader project.
Provides common file operations like read/write JSON, directory management, etc.
"""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .logger import get_logger

logger = get_logger(__name__)


def read_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Read JSON file and return as dictionary.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dictionary containing JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.debug(f"Successfully read JSON from {file_path}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {e}")
        raise


def write_json(
    data: Dict[str, Any],
    file_path: Union[str, Path],
    indent: int = 2,
    ensure_ascii: bool = False
) -> None:
    """
    Write dictionary to JSON file.
    
    Args:
        data: Dictionary to write
        file_path: Path to output JSON file
        indent: Number of spaces for indentation
        ensure_ascii: If True, escape non-ASCII characters
    """
    file_path = Path(file_path)
    
    # Create parent directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
        logger.debug(f"Successfully wrote JSON to {file_path}")
    except Exception as e:
        logger.error(f"Failed to write JSON to {file_path}: {e}")
        raise


def read_text(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """
    Read text file and return as string.
    
    Args:
        file_path: Path to text file
        encoding: File encoding
        
    Returns:
        File contents as string
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Text file not found: {file_path}")
    
    with open(file_path, 'r', encoding=encoding) as f:
        content = f.read()
    
    logger.debug(f"Successfully read text from {file_path}")
    return content


def write_text(
    content: str,
    file_path: Union[str, Path],
    encoding: str = 'utf-8'
) -> None:
    """
    Write string to text file.
    
    Args:
        content: String content to write
        file_path: Path to output text file
        encoding: File encoding
    """
    file_path = Path(file_path)
    
    # Create parent directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding=encoding) as f:
        f.write(content)
    
    logger.debug(f"Successfully wrote text to {file_path}")


def read_lines(
    file_path: Union[str, Path],
    encoding: str = 'utf-8',
    strip: bool = True
) -> List[str]:
    """
    Read text file and return as list of lines.
    
    Args:
        file_path: Path to text file
        encoding: File encoding
        strip: Whether to strip whitespace from each line
        
    Returns:
        List of lines from file
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Text file not found: {file_path}")
    
    with open(file_path, 'r', encoding=encoding) as f:
        lines = f.readlines()
    
    if strip:
        lines = [line.strip() for line in lines]
    
    logger.debug(f"Successfully read {len(lines)} lines from {file_path}")
    return lines


def write_lines(
    lines: List[str],
    file_path: Union[str, Path],
    encoding: str = 'utf-8',
    add_newline: bool = True
) -> None:
    """
    Write list of lines to text file.
    
    Args:
        lines: List of strings to write
        file_path: Path to output text file
        encoding: File encoding
        add_newline: Whether to add newline after each line
    """
    file_path = Path(file_path)
    
    # Create parent directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding=encoding) as f:
        for line in lines:
            f.write(line)
            if add_newline and not line.endswith('\n'):
                f.write('\n')
    
    logger.debug(f"Successfully wrote {len(lines)} lines to {file_path}")


def ensure_dir(dir_path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        dir_path: Path to directory
        
    Returns:
        Path object for the directory
    """
    dir_path = Path(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured directory exists: {dir_path}")
    return dir_path


def file_exists(file_path: Union[str, Path]) -> bool:
    """
    Check if file exists.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file exists, False otherwise
    """
    return Path(file_path).is_file()


def dir_exists(dir_path: Union[str, Path]) -> bool:
    """
    Check if directory exists.
    
    Args:
        dir_path: Path to directory
        
    Returns:
        True if directory exists, False otherwise
    """
    return Path(dir_path).is_dir()


def list_files(
    dir_path: Union[str, Path],
    pattern: str = "*",
    recursive: bool = False
) -> List[Path]:
    """
    List files in directory matching pattern.
    
    Args:
        dir_path: Path to directory
        pattern: Glob pattern to match (default: "*" for all files)
        recursive: If True, search recursively
        
    Returns:
        List of Path objects for matching files
    """
    dir_path = Path(dir_path)
    
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {dir_path}")
    
    if recursive:
        files = list(dir_path.rglob(pattern))
    else:
        files = list(dir_path.glob(pattern))
    
    # Filter to only files (not directories)
    files = [f for f in files if f.is_file()]
    
    logger.debug(f"Found {len(files)} files in {dir_path} with pattern '{pattern}'")
    return files


def copy_file(
    src_path: Union[str, Path],
    dst_path: Union[str, Path],
    overwrite: bool = False
) -> None:
    """
    Copy file from source to destination.
    
    Args:
        src_path: Source file path
        dst_path: Destination file path
        overwrite: If True, overwrite destination if it exists
        
    Raises:
        FileNotFoundError: If source file doesn't exist
        FileExistsError: If destination exists and overwrite is False
    """
    src_path = Path(src_path)
    dst_path = Path(dst_path)
    
    if not src_path.is_file():
        raise FileNotFoundError(f"Source file not found: {src_path}")
    
    if dst_path.exists() and not overwrite:
        raise FileExistsError(f"Destination already exists: {dst_path}")
    
    # Ensure destination directory exists
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    
    shutil.copy2(src_path, dst_path)
    logger.debug(f"Copied file from {src_path} to {dst_path}")


def delete_file(file_path: Union[str, Path]) -> None:
    """
    Delete file if it exists.
    
    Args:
        file_path: Path to file to delete
    """
    file_path = Path(file_path)
    
    if file_path.is_file():
        file_path.unlink()
        logger.debug(f"Deleted file: {file_path}")


def delete_dir(dir_path: Union[str, Path], recursive: bool = True) -> None:
    """
    Delete directory.
    
    Args:
        dir_path: Path to directory to delete
        recursive: If True, delete directory and all contents
    """
    dir_path = Path(dir_path)
    
    if not dir_path.is_dir():
        return
    
    if recursive:
        shutil.rmtree(dir_path)
        logger.debug(f"Deleted directory recursively: {dir_path}")
    else:
        dir_path.rmdir()
        logger.debug(f"Deleted empty directory: {dir_path}")


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes
    """
    file_path = Path(file_path)
    
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    return file_path.stat().st_size


def validate_path(
    file_path: Union[str, Path],
    must_exist: bool = False,
    must_be_file: bool = False,
    must_be_dir: bool = False
) -> Path:
    """
    Validate path and return Path object.
    
    Args:
        file_path: Path to validate
        must_exist: If True, raise error if path doesn't exist
        must_be_file: If True, raise error if path is not a file
        must_be_dir: If True, raise error if path is not a directory
        
    Returns:
        Path object
        
    Raises:
        FileNotFoundError: If must_exist is True and path doesn't exist
        ValueError: If path doesn't meet requirements
    """
    file_path = Path(file_path)
    
    if must_exist and not file_path.exists():
        raise FileNotFoundError(f"Path does not exist: {file_path}")
    
    if must_be_file and not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    if must_be_dir and not file_path.is_dir():
        raise ValueError(f"Path is not a directory: {file_path}")
    
    return file_path
