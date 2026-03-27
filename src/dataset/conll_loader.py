"""
CONLL format dataset loader for prescription NER training.
Handles BIO tagging and creates PyTorch datasets.
"""

import torch
from torch.utils.data import Dataset
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Union
from dataclasses import dataclass

from ..utils.config import get_paths, get_model_config
from ..utils.logger import get_logger
from ..utils.file_utils import read_lines, file_exists

logger = get_logger(__name__)


@dataclass
class ConllExample:
    """Represents a single example from CONLL dataset."""
    tokens: List[str]
    labels: List[str]
    
    def __len__(self):
        return len(self.tokens)


class ConllDatasetError(Exception):
    """Exception for CONLL dataset errors."""
    pass


def parse_conll_file(file_path: Union[str, Path]) -> List[ConllExample]:
    """
    Parse CONLL format file into examples.
    
    CONLL format:
    - Each line contains: token<space>label
    - Empty lines separate sentences/examples
    - Comments start with #
    
    Args:
        file_path: Path to CONLL format file
        
    Returns:
        List of ConllExample objects
        
    Raises:
        ConllDatasetError: If file format is invalid
    """
    try:
        file_path = Path(file_path)
        
        if not file_exists(file_path):
            raise ConllDatasetError(f"CONLL file not found: {file_path}")
        
        logger.info(f"Parsing CONLL file: {file_path}")
        
        lines = read_lines(file_path, strip=True)
        
        examples = []
        current_tokens = []
        current_labels = []
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments
            if line.startswith('#'):
                continue
            
            # Empty line marks end of example
            if not line:
                if current_tokens:
                    examples.append(ConllExample(
                        tokens=current_tokens,
                        labels=current_labels
                    ))
                    current_tokens = []
                    current_labels = []
                continue
            
            # Parse token and label
            parts = line.split()
            
            if len(parts) < 2:
                logger.warning(f"Line {line_num}: Invalid format (expected 'token label'), got: {line}")
                continue
            
            token = parts[0]
            label = parts[1]
            
            current_tokens.append(token)
            current_labels.append(label)
        
        # Don't forget last example if file doesn't end with empty line
        if current_tokens:
            examples.append(ConllExample(
                tokens=current_tokens,
                labels=current_labels
            ))
        
        logger.info(f"Parsed {len(examples)} examples from {file_path}")
        
        if not examples:
            raise ConllDatasetError(f"No examples found in {file_path}")
        
        return examples
        
    except Exception as e:
        if isinstance(e, ConllDatasetError):
            raise
        logger.error(f"Failed to parse CONLL file: {str(e)}")
        raise ConllDatasetError(f"Error parsing CONLL file: {str(e)}") from e


class PrescriptionDataset(Dataset):
    """PyTorch Dataset for prescription NER from CONLL format."""
    
    def __init__(
        self,
        file_path: Union[str, Path],
        tokenizer,
        label_map: Dict[str, int],
        max_length: int = 128
    ):
        """
        Initialize dataset.
        
        Args:
            file_path: Path to CONLL format file
            tokenizer: HuggingFace tokenizer
            label_map: Mapping from label strings to IDs
            max_length: Maximum sequence length
        """
        self.file_path = Path(file_path)
        self.tokenizer = tokenizer
        self.label_map = label_map
        self.max_length = max_length
        
        logger.info(f"Loading dataset from {self.file_path}")
        
        # Parse CONLL file
        self.examples = parse_conll_file(self.file_path)
        
        logger.info(f"Dataset loaded: {len(self.examples)} examples")
    
    def __len__(self) -> int:
        """Return number of examples."""
        return len(self.examples)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get a single example.
        
        Args:
            idx: Example index
            
        Returns:
            Dictionary with input_ids, attention_mask, and labels
        """
        example = self.examples[idx]
        
        # Tokenize with alignment
        encoding = self.tokenizer(
            example.tokens,
            is_split_into_words=True,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        # Align labels with subword tokens
        labels = self._align_labels_with_tokens(
            example.labels,
            encoding.word_ids()
        )
        
        # Pad labels to max_length
        labels = labels + [-100] * (self.max_length - len(labels))
        labels = labels[:self.max_length]
        
        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'labels': torch.tensor(labels, dtype=torch.long)
        }
    
    def _align_labels_with_tokens(
        self,
        labels: List[str],
        word_ids: List[Optional[int]]
    ) -> List[int]:
        """
        Align labels with subword tokens.
        
        Args:
            labels: Original labels for each word
            word_ids: Word IDs for each subword token (from tokenizer)
            
        Returns:
            List of label IDs aligned with tokens
        """
        aligned_labels = []
        previous_word_idx = None
        
        for word_idx in word_ids:
            # Special tokens get -100 (ignored in loss)
            if word_idx is None:
                aligned_labels.append(-100)
            
            # First subword of a word gets the label
            elif word_idx != previous_word_idx:
                label = labels[word_idx]
                label_id = self.label_map.get(label, 0)  # Default to 'O' (0)
                aligned_labels.append(label_id)
            
            # Subsequent subwords of same word get -100
            else:
                aligned_labels.append(-100)
            
            previous_word_idx = word_idx
        
        return aligned_labels
    
    def get_label_distribution(self) -> Dict[str, int]:
        """
        Compute distribution of labels in dataset.
        
        Returns:
            Dictionary mapping label to count
        """
        label_counts = {}
        
        for example in self.examples:
            for label in example.labels:
                label_counts[label] = label_counts.get(label, 0) + 1
        
        return label_counts


def load_conll_datasets(
    tokenizer,
    label_map: Dict[str, int],
    train_path: Optional[Union[str, Path]] = None,
    dev_path: Optional[Union[str, Path]] = None,
    test_path: Optional[Union[str, Path]] = None,
    max_length: int = 128
) -> Dict[str, PrescriptionDataset]:
    """
    Load train/dev/test datasets from CONLL files.
    
    Args:
        tokenizer: HuggingFace tokenizer
        label_map: Mapping from label strings to IDs
        train_path: Optional path to training data
        dev_path: Optional path to dev data
        test_path: Optional path to test data
        max_length: Maximum sequence length
        
    Returns:
        Dictionary with 'train', 'dev', 'test' datasets (if paths provided)
    """
    paths = get_paths()
    datasets = {}
    
    # Use default paths if not provided
    if train_path is None:
        train_path = paths.conll_train
    if dev_path is None:
        dev_path = paths.conll_dev
    if test_path is None:
        test_path = paths.conll_test
    
    # Load datasets
    if file_exists(train_path):
        logger.info(f"Loading training dataset from {train_path}")
        datasets['train'] = PrescriptionDataset(
            train_path, tokenizer, label_map, max_length
        )
    else:
        logger.warning(f"Training data not found at {train_path}")
    
    if file_exists(dev_path):
        logger.info(f"Loading dev dataset from {dev_path}")
        datasets['dev'] = PrescriptionDataset(
            dev_path, tokenizer, label_map, max_length
        )
    else:
        logger.warning(f"Dev data not found at {dev_path}")
    
    if file_exists(test_path):
        logger.info(f"Loading test dataset from {test_path}")
        datasets['test'] = PrescriptionDataset(
            test_path, tokenizer, label_map, max_length
        )
    else:
        logger.warning(f"Test data not found at {test_path}")
    
    if not datasets:
        raise ConllDatasetError("No datasets could be loaded. Please check file paths.")
    
    return datasets


def create_label_mappings() -> Tuple[Dict[str, int], Dict[int, str]]:
    """
    Create label mappings from label_map.json.
    
    Returns:
        Tuple of (label2id, id2label) dictionaries
    """
    from ..utils.file_utils import read_json
    
    paths = get_paths()
    
    try:
        label2id = read_json(paths.label_map_path)
        id2label = {int(v): k for k, v in label2id.items()}
        
        logger.info(f"Loaded {len(label2id)} label mappings")
        return label2id, id2label
        
    except Exception as e:
        logger.error(f"Failed to load label mappings: {str(e)}")
        raise ConllDatasetError(f"Could not load label mappings: {str(e)}") from e
