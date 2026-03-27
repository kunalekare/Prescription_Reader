"""
Training module for fine-tuning BioBERT on prescription NER data.
Implements training loop with validation, checkpointing, and early stopping.
"""

import torch
from torch.utils.data import DataLoader
from torch.optim import AdamW
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    get_linear_schedule_with_warmup
)
from tqdm import tqdm
import os
from pathlib import Path
from typing import Dict, Optional, Tuple
import json
from datetime import datetime

from ..dataset.conll_loader import (
    load_conll_datasets,
    create_label_mappings,
    ConllDatasetError
)
from ..utils.config import get_config, get_model_config, get_paths
from ..utils.logger import get_logger
from ..utils.file_utils import write_json, ensure_dir

logger = get_logger(__name__)


class TrainingError(Exception):
    """Exception for training errors."""
    pass


class EarlyStopping:
    """Early stopping to prevent overfitting."""
    
    def __init__(self, patience: int = 3, delta: float = 0.001):
        """
        Initialize early stopping.
        
        Args:
            patience: How many epochs to wait before stopping
            delta: Minimum change to qualify as improvement
        """
        self.patience = patience
        self.delta = delta
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.best_loss = float('inf')
        
        logger.info(f"Early stopping: patience={patience}, delta={delta}")
    
    def __call__(self, val_loss: float) -> bool:
        """
        Check if should stop training.
        
        Args:
            val_loss: Current validation loss
            
        Returns:
            True if should stop, False otherwise
        """
        score = -val_loss
        
        if self.best_score is None:
            self.best_score = score
            self.best_loss = val_loss
        elif score < self.best_score + self.delta:
            self.counter += 1
            logger.info(f"EarlyStopping counter: {self.counter} / {self.patience}")
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.best_loss = val_loss
            self.counter = 0
        
        return self.early_stop


class PrescriptionNERTrainer:
    """Trainer for prescription NER model."""
    
    def __init__(
        self,
        output_dir: Optional[Path] = None,
        model_name: Optional[str] = None
    ):
        """
        Initialize trainer.
        
        Args:
            output_dir: Directory to save model and checkpoints
            model_name: Pretrained model name to fine-tune
        """
        self.config = get_model_config()
        self.paths = get_paths()
        
        # Set output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = self.paths.biobert_model_path
        
        # Set model name
        self.model_name = model_name or self.config.pretrained_model_name
        
        # Set device
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() and self.config.device == "cuda" 
            else "cpu"
        )
        logger.info(f"Using device: {self.device}")
        
        # Initialize components
        self.tokenizer = None
        self.model = None
        self.label2id = None
        self.id2label = None
        
        # Training state
        self.global_step = 0
        self.best_val_loss = float('inf')
        self.training_history = {
            'train_loss': [],
            'val_loss': [],
            'learning_rates': []
        }
    
    def setup(self):
        """Load label mappings and initialize model."""
        try:
            logger.info("Setting up trainer...")
            
            # Load label mappings
            logger.info("Loading label mappings...")
            self.label2id, self.id2label = create_label_mappings()
            num_labels = len(self.label2id)
            logger.info(f"Number of labels: {num_labels}")
            
            # Load tokenizer
            logger.info(f"Loading tokenizer from {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Load model
            logger.info(f"Loading model from {self.model_name}...")
            self.model = AutoModelForTokenClassification.from_pretrained(
                self.model_name,
                num_labels=num_labels,
                id2label=self.id2label,
                label2id=self.label2id
            )
            
            # Move to device
            self.model.to(self.device)
            
            logger.info("Trainer setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup trainer: {str(e)}")
            raise TrainingError(f"Trainer setup failed: {str(e)}") from e
    
    def train(
        self,
        train_path: Optional[Path] = None,
        dev_path: Optional[Path] = None,
        num_epochs: Optional[int] = None,
        batch_size: Optional[int] = None,
        learning_rate: Optional[float] = None
    ) -> Dict:
        """
        Train the model.
        
        Args:
            train_path: Path to training data (uses config default if None)
            dev_path: Path to dev data (uses config default if None)
            num_epochs: Number of epochs (uses config default if None)
            batch_size: Batch size (uses config default if None)
            learning_rate: Learning rate (uses config default if None)
            
        Returns:
            Dictionary with training metrics
        """
        try:
            # Setup if not done
            if self.model is None:
                self.setup()
            
            # Use config defaults if not provided
            num_epochs = num_epochs or self.config.num_epochs
            batch_size = batch_size or self.config.batch_size
            learning_rate = learning_rate or self.config.learning_rate
            
            logger.info(f"Training configuration:")
            logger.info(f"  Epochs: {num_epochs}")
            logger.info(f"  Batch size: {batch_size}")
            logger.info(f"  Learning rate: {learning_rate}")
            
            # Load datasets
            logger.info("Loading datasets...")
            datasets = load_conll_datasets(
                self.tokenizer,
                self.label2id,
                train_path=train_path,
                dev_path=dev_path,
                max_length=self.config.max_length
            )
            
            if 'train' not in datasets:
                raise TrainingError("Training dataset not found")
            
            train_dataset = datasets['train']
            dev_dataset = datasets.get('dev', None)
            
            logger.info(f"Train examples: {len(train_dataset)}")
            if dev_dataset:
                logger.info(f"Dev examples: {len(dev_dataset)}")
            
            # Create dataloaders
            train_loader = DataLoader(
                train_dataset,
                batch_size=batch_size,
                shuffle=True,
                num_workers=0  # Windows compatibility
            )
            
            dev_loader = None
            if dev_dataset:
                dev_loader = DataLoader(
                    dev_dataset,
                    batch_size=batch_size,
                    shuffle=False,
                    num_workers=0
                )
            
            # Setup optimizer and scheduler
            optimizer = AdamW(
                self.model.parameters(),
                lr=learning_rate,
                eps=self.config.adam_epsilon,
                weight_decay=self.config.weight_decay
            )
            
            total_steps = len(train_loader) * num_epochs
            scheduler = get_linear_schedule_with_warmup(
                optimizer,
                num_warmup_steps=self.config.warmup_steps,
                num_training_steps=total_steps
            )
            
            # Early stopping
            early_stopping = EarlyStopping(
                patience=self.config.early_stopping_patience,
                delta=self.config.early_stopping_delta
            )
            
            # Training loop
            logger.info("Starting training...")
            
            for epoch in range(num_epochs):
                logger.info(f"\n{'='*50}")
                logger.info(f"Epoch {epoch + 1}/{num_epochs}")
                logger.info(f"{'='*50}")
                
                # Train
                train_loss = self._train_epoch(
                    train_loader,
                    optimizer,
                    scheduler
                )
                
                logger.info(f"Average training loss: {train_loss:.4f}")
                self.training_history['train_loss'].append(train_loss)
                
                # Validate
                if dev_loader:
                    val_loss = self._validate_epoch(dev_loader)
                    logger.info(f"Validation loss: {val_loss:.4f}")
                    self.training_history['val_loss'].append(val_loss)
                    
                    # Check early stopping
                    if early_stopping(val_loss):
                        logger.info("Early stopping triggered")
                        break
                    
                    # Save best model
                    if val_loss < self.best_val_loss:
                        self.best_val_loss = val_loss
                        logger.info(f"New best validation loss: {val_loss:.4f}")
                        self.save_model(self.output_dir, is_best=True)
                
                # Save checkpoint
                if (epoch + 1) % 2 == 0:
                    checkpoint_dir = self.paths.checkpoint_dir / f"epoch_{epoch+1}"
                    self.save_model(checkpoint_dir, is_checkpoint=True, epoch=epoch+1)
            
            # Save final model
            logger.info("Saving final model...")
            self.save_model(self.output_dir)
            
            # Save training history
            self._save_training_history()
            
            logger.info("Training complete!")
            
            return {
                'final_train_loss': self.training_history['train_loss'][-1],
                'final_val_loss': self.training_history['val_loss'][-1] if self.training_history['val_loss'] else None,
                'best_val_loss': self.best_val_loss,
                'epochs_trained': len(self.training_history['train_loss'])
            }
            
        except ConllDatasetError as e:
            logger.error(f"Dataset error: {str(e)}")
            raise TrainingError(f"Failed to load datasets: {str(e)}") from e
        
        except Exception as e:
            logger.error(f"Training failed: {str(e)}", exc_info=True)
            raise TrainingError(f"Training failed: {str(e)}") from e
    
    def _train_epoch(
        self,
        train_loader: DataLoader,
        optimizer,
        scheduler
    ) -> float:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0
        
        progress_bar = tqdm(train_loader, desc="Training")
        
        for step, batch in enumerate(progress_bar):
            # Move batch to device
            batch = {k: v.to(self.device) for k, v in batch.items()}
            
            # Forward pass
            outputs = self.model(**batch)
            loss = outputs.loss
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                self.config.max_grad_norm
            )
            
            # Update weights
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
            
            # Update metrics
            total_loss += loss.item()
            self.global_step += 1
            
            # Update progress bar
            progress_bar.set_postfix({'loss': loss.item()})
            
            # Log periodically
            if self.global_step % self.config.logging_steps == 0:
                current_lr = scheduler.get_last_lr()[0]
                self.training_history['learning_rates'].append(current_lr)
                logger.debug(f"Step {self.global_step}: loss={loss.item():.4f}, lr={current_lr:.2e}")
        
        return total_loss / len(train_loader)
    
    def _validate_epoch(self, dev_loader: DataLoader) -> float:
        """Validate for one epoch."""
        self.model.eval()
        total_loss = 0
        
        with torch.no_grad():
            for batch in tqdm(dev_loader, desc="Validation"):
                # Move batch to device
                batch = {k: v.to(self.device) for k, v in batch.items()}
                
                # Forward pass
                outputs = self.model(**batch)
                loss = outputs.loss
                
                total_loss += loss.item()
        
        return total_loss / len(dev_loader)
    
    def save_model(
        self,
        output_dir: Path,
        is_best: bool = False,
        is_checkpoint: bool = False,
        epoch: Optional[int] = None
    ):
        """Save model and tokenizer."""
        output_dir = Path(output_dir)
        ensure_dir(output_dir)
        
        logger.info(f"Saving model to {output_dir}")
        
        # Save model and tokenizer
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        # Save metadata
        metadata = {
            'model_name': self.model_name,
            'num_labels': len(self.label2id),
            'label2id': self.label2id,
            'id2label': self.id2label,
            'config': self.config.__dict__ if hasattr(self.config, '__dict__') else {},
            'timestamp': datetime.now().isoformat(),
            'global_step': self.global_step,
            'best_val_loss': self.best_val_loss
        }
        
        if epoch is not None:
            metadata['epoch'] = epoch
        
        write_json(metadata, output_dir / 'training_metadata.json')
        
        if is_best:
            logger.info("✓ Saved best model")
        elif is_checkpoint:
            logger.info(f"✓ Saved checkpoint (epoch {epoch})")
    
    def _save_training_history(self):
        """Save training history for visualization."""
        history_path = self.paths.metrics_dir / 'training_history.json'
        write_json(self.training_history, history_path)
        logger.info(f"Saved training history to {history_path}")


def train_model(
    train_path: Optional[Path] = None,
    dev_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    **kwargs
) -> Dict:
    """
    Convenience function to train model.
    
    Args:
        train_path: Path to training data
        dev_path: Path to dev data
        output_dir: Output directory for model
        **kwargs: Additional training arguments
        
    Returns:
        Training metrics dictionary
    """
    trainer = PrescriptionNERTrainer(output_dir=output_dir)
    return trainer.train(
        train_path=train_path,
        dev_path=dev_path,
        **kwargs
    )


if __name__ == "__main__":
    # Example usage
    logger.info("Starting training...")
    results = train_model()
    logger.info(f"Training results: {results}")
