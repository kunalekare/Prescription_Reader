"""
Evaluation module for computing NER performance metrics.
Provides entity-level F1, precision, recall and confusion matrix.
"""

import torch
from torch.utils.data import DataLoader
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import numpy as np
from collections import defaultdict
from seqeval.metrics import (
    f1_score,
    precision_score,
    recall_score,
    classification_report
)

from ..dataset.conll_loader import load_conll_datasets, create_label_mappings
from ..utils.config import get_paths, get_model_config
from ..utils.logger import get_logger
from ..utils.file_utils import write_json, ensure_dir

logger = get_logger(__name__)


class EvaluationError(Exception):
    """Exception for evaluation errors."""
    pass


class ModelEvaluator:
    """Evaluator for NER models."""
    
    def __init__(self, model, tokenizer, label2id: Dict, id2label: Dict):
        """
        Initialize evaluator.
        
        Args:
            model: Trained model
            tokenizer: Tokenizer
            label2id: Label to ID mapping
            id2label: ID to label mapping
        """
        self.model = model
        self.tokenizer = tokenizer
        self.label2id = label2id
        self.id2label = id2label
        self.config = get_model_config()
        self.paths = get_paths()
        
        # Set device
        self.device = next(model.parameters()).device
        logger.info(f"Evaluator using device: {self.device}")
    
    def evaluate(
        self,
        test_path: Optional[Path] = None,
        batch_size: Optional[int] = None
    ) -> Dict:
        """
        Evaluate model on test set.
        
        Args:
            test_path: Path to test data
            batch_size: Batch size for evaluation
            
        Returns:
            Dictionary with evaluation metrics
        """
        try:
            logger.info("Starting evaluation...")
            
            batch_size = batch_size or self.config.batch_size
            
            # Load test dataset
            datasets = load_conll_datasets(
                self.tokenizer,
                self.label2id,
                test_path=test_path,
                max_length=self.config.max_length
            )
            
            if 'test' not in datasets:
                raise EvaluationError("Test dataset not found")
            
            test_dataset = datasets['test']
            logger.info(f"Test examples: {len(test_dataset)}")
            
            # Create dataloader
            test_loader = DataLoader(
                test_dataset,
                batch_size=batch_size,
                shuffle=False,
                num_workers=0
            )
            
            # Get predictions
            true_labels, pred_labels = self._get_predictions(test_loader)
            
            # Compute metrics
            metrics = self._compute_metrics(true_labels, pred_labels)
            
            # Save results
            self._save_results(metrics, true_labels, pred_labels)
            
            logger.info("Evaluation complete!")
            return metrics
            
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            raise EvaluationError(f"Evaluation failed: {str(e)}") from e
    
    def _get_predictions(
        self,
        dataloader: DataLoader
    ) -> Tuple[List[List[str]], List[List[str]]]:
        """
        Get predictions from model.
        
        Returns:
            Tuple of (true_labels, predicted_labels)
        """
        self.model.eval()
        
        all_true_labels = []
        all_pred_labels = []
        
        logger.info("Generating predictions...")
        
        with torch.no_grad():
            for batch in dataloader:
                # Move to device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels']
                
                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                
                logits = outputs.logits
                predictions = torch.argmax(logits, dim=-1)
                
                # Convert to labels (remove padding and special tokens)
                for i in range(len(labels)):
                    true_seq = []
                    pred_seq = []
                    
                    for j in range(len(labels[i])):
                        label_id = labels[i][j].item()
                        
                        # Skip padding and special tokens (-100)
                        if label_id == -100:
                            continue
                        
                        true_label = self.id2label.get(label_id, 'O')
                        pred_label = self.id2label.get(predictions[i][j].item(), 'O')
                        
                        true_seq.append(true_label)
                        pred_seq.append(pred_label)
                    
                    all_true_labels.append(true_seq)
                    all_pred_labels.append(pred_seq)
        
        logger.info(f"Generated predictions for {len(all_true_labels)} sequences")
        return all_true_labels, all_pred_labels
    
    def _compute_metrics(
        self,
        true_labels: List[List[str]],
        pred_labels: List[List[str]]
    ) -> Dict:
        """
        Compute evaluation metrics.
        
        Args:
            true_labels: True labels
            pred_labels: Predicted labels
            
        Returns:
            Dictionary with metrics
        """
        logger.info("Computing metrics...")
        
        # Overall metrics
        precision = precision_score(true_labels, pred_labels)
        recall = recall_score(true_labels, pred_labels)
        f1 = f1_score(true_labels, pred_labels)
        
        # Detailed report
        report = classification_report(
            true_labels,
            pred_labels,
            output_dict=True,
            zero_division=0
        )
        
        metrics = {
            'overall': {
                'precision': float(precision),
                'recall': float(recall),
                'f1': float(f1)
            },
            'per_entity': {}
        }
        
        # Extract entity-level metrics
        for label, scores in report.items():
            if isinstance(scores, dict) and label not in ['macro avg', 'weighted avg', 'micro avg']:
                metrics['per_entity'][label] = {
                    'precision': float(scores.get('precision', 0)),
                    'recall': float(scores.get('recall', 0)),
                    'f1-score': float(scores.get('f1-score', 0)),
                    'support': int(scores.get('support', 0))
                }
        
        # Log results
        logger.info(f"Overall F1: {f1:.4f}")
        logger.info(f"Overall Precision: {precision:.4f}")
        logger.info(f"Overall Recall: {recall:.4f}")
        
        return metrics
    
    def _save_results(
        self,
        metrics: Dict,
        true_labels: List[List[str]],
        pred_labels: List[List[str]]
    ):
        """Save evaluation results."""
        ensure_dir(self.paths.metrics_dir)
        
        # Save metrics
        metrics_path = self.paths.metrics_dir / 'evaluation_results.json'
        write_json(metrics, metrics_path)
        logger.info(f"Saved metrics to {metrics_path}")
        
        # Save detailed classification report
        report_path = self.paths.metrics_dir / 'classification_report.txt'
        report_text = classification_report(true_labels, pred_labels)
        
        with open(report_path, 'w') as f:
            f.write(report_text)
        logger.info(f"Saved classification report to {report_path}")
    
    def compute_confusion_matrix(
        self,
        true_labels: List[List[str]],
        pred_labels: List[List[str]]
    ) -> Dict:
        """
        Compute confusion matrix for entity types.
        
        Args:
            true_labels: True labels
            pred_labels: Predicted labels
            
        Returns:
            Dictionary representing confusion matrix
        """
        confusion = defaultdict(lambda: defaultdict(int))
        
        for true_seq, pred_seq in zip(true_labels, pred_labels):
            for true_label, pred_label in zip(true_seq, pred_seq):
                confusion[true_label][pred_label] += 1
        
        # Convert to regular dict
        confusion_dict = {
            true_label: dict(pred_counts)
            for true_label, pred_counts in confusion.items()
        }
        
        return confusion_dict


def evaluate_model(
    model,
    tokenizer,
    test_path: Optional[Path] = None,
    **kwargs
) -> Dict:
    """
    Convenience function to evaluate model.
    
    Args:
        model: Trained model
        tokenizer: Tokenizer
        test_path: Path to test data
        **kwargs: Additional arguments
        
    Returns:
        Evaluation metrics
    """
    # Load label mappings
    label2id, id2label = create_label_mappings()
    
    # Create evaluator
    evaluator = ModelEvaluator(model, tokenizer, label2id, id2label)
    
    # Run evaluation
    return evaluator.evaluate(test_path=test_path, **kwargs)
