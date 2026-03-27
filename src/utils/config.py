"""
Configuration management for Prescription Reader project.
Centralizes all configuration parameters including paths, API settings, and hyperparameters.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class PathConfig:
    """Configuration for file paths and directories."""
    
    # Project root
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)
    
    # Data paths
    data_dir: Path = field(init=False)
    conll_train: Path = field(init=False)
    conll_dev: Path = field(init=False)
    conll_test: Path = field(init=False)
    prescription_data_dir: Path = field(init=False)
    
    # Model paths
    models_dir: Path = field(init=False)
    label_map_path: Path = field(init=False)
    id2label_path: Path = field(init=False)
    biobert_model_path: Path = field(init=False)
    checkpoint_dir: Path = field(init=False)
    
    # Output paths
    outputs_dir: Path = field(init=False)
    predictions_dir: Path = field(init=False)
    metrics_dir: Path = field(init=False)
    visualizations_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    
    def __post_init__(self):
        """Initialize all paths after object creation."""
        # Data paths
        self.data_dir = self.project_root / "data" / "custom_indian"
        self.conll_train = self.data_dir / "train.conll"
        self.conll_dev = self.data_dir / "dev.conll"
        self.conll_test = self.data_dir / "test.conll"
        self.prescription_data_dir = self.project_root / "Prescrption_Data"
        
        # Model paths
        self.models_dir = self.project_root / "models"
        self.label_map_path = self.models_dir / "label_map.json"
        self.id2label_path = self.models_dir / "id2label.json"
        self.biobert_model_path = self.models_dir / "biobert_prescription"
        self.checkpoint_dir = self.models_dir / "checkpoints"
        
        # Output paths
        self.outputs_dir = self.project_root / "outputs"
        self.predictions_dir = self.outputs_dir / "predictions"
        self.metrics_dir = self.outputs_dir / "metrics"
        self.visualizations_dir = self.outputs_dir / "visualizations"
        self.logs_dir = self.outputs_dir / "logs"
        
        # Create directories if they don't exist
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories."""
        for dir_path in [
            self.checkpoint_dir,
            self.predictions_dir,
            self.metrics_dir,
            self.visualizations_dir,
            self.logs_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)


@dataclass
class OCRConfig:
    """Configuration for OCR API settings."""
    
    api_key: str = field(default_factory=lambda: os.getenv("SARVAM_API_KEY", ""))
    # Sarvam Vision API endpoint - based on model name "sarvam-vision"
    api_url: str = "https://api.sarvam.ai/v1/sarvam-vision"
    timeout: int = 30
    max_retries: int = 3
    
    def __post_init__(self):
        """Validate API key is present."""
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY not found in environment variables")


@dataclass
class ModelConfig:
    """Configuration for NER model settings."""
    
    # Pre-trained model
    pretrained_model_name: str = "dmis-lab/biobert-base-cased-v1.2"
    
    # Training hyperparameters
    learning_rate: float = 2e-5
    num_epochs: int = 10
    batch_size: int = 16
    max_length: int = 128
    warmup_steps: int = 500
    weight_decay: float = 0.01
    gradient_accumulation_steps: int = 1
    
    # Optimization
    adam_epsilon: float = 1e-8
    max_grad_norm: float = 1.0
    
    # Early stopping
    early_stopping_patience: int = 3
    early_stopping_delta: float = 0.001
    
    # Validation
    eval_steps: int = 100
    save_steps: int = 500
    logging_steps: int = 50
    
    # Device
    device: str = "cuda" if os.getenv("USE_CUDA", "auto") == "auto" else "cpu"
    
    # Random seed for reproducibility
    random_seed: int = 42


@dataclass
class EvaluationConfig:
    """Configuration for evaluation settings."""
    
    # Metrics to compute
    compute_entity_level_metrics: bool = True
    compute_confusion_matrix: bool = True
    
    # Cross-validation
    k_folds: int = 5
    
    # Confidence threshold
    confidence_threshold: float = 0.5


@dataclass
class InferenceConfig:
    """Configuration for inference settings."""
    
    # Batch processing
    batch_size: int = 8
    
    # Post-processing
    merge_subwords: bool = True
    filter_low_confidence: bool = True
    confidence_threshold: float = 0.7
    
    # Output format
    output_format: str = "json"  # json, csv, or dict


@dataclass
class LoggingConfig:
    """Configuration for logging settings."""
    
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_logging: bool = True
    file_logging: bool = True


@dataclass
class Config:
    """Main configuration class combining all sub-configurations."""
    
    paths: PathConfig = field(default_factory=PathConfig)
    ocr: OCRConfig = field(default_factory=OCRConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "paths": self.paths.__dict__,
            "ocr": self.ocr.__dict__,
            "model": self.model.__dict__,
            "evaluation": self.evaluation.__dict__,
            "inference": self.inference.__dict__,
            "logging": self.logging.__dict__,
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        """Create config from dictionary."""
        return cls(
            paths=PathConfig(**config_dict.get("paths", {})),
            ocr=OCRConfig(**config_dict.get("ocr", {})),
            model=ModelConfig(**config_dict.get("model", {})),
            evaluation=EvaluationConfig(**config_dict.get("evaluation", {})),
            inference=InferenceConfig(**config_dict.get("inference", {})),
            logging=LoggingConfig(**config_dict.get("logging", {})),
        )


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def set_config(config: Config):
    """Set the global configuration instance."""
    global _config
    _config = config


# Convenience function to get specific configs
def get_paths() -> PathConfig:
    """Get path configuration."""
    return get_config().paths


def get_ocr_config() -> OCRConfig:
    """Get OCR configuration."""
    return get_config().ocr


def get_model_config() -> ModelConfig:
    """Get model configuration."""
    return get_config().model


def get_evaluation_config() -> EvaluationConfig:
    """Get evaluation configuration."""
    return get_config().evaluation


def get_inference_config() -> InferenceConfig:
    """Get inference configuration."""
    return get_config().inference


def get_logging_config() -> LoggingConfig:
    """Get logging configuration."""
    return get_config().logging
