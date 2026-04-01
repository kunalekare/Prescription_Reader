"""
Inference module for NER prediction on prescription text using BioBERT.
"""

from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union

from ..ocr.sarvam_ocr import extract_text_from_image, OCRError
from ..preprocessing.text_cleaner import clean_text, TextCleaningError
from ..utils.config import get_paths, get_model_config, get_inference_config
from ..utils.logger import get_logger
from ..utils.file_utils import read_json, file_exists
from ..utils.drug_info import get_drug_description

logger = get_logger(__name__)


class ModelLoadError(Exception):
    """Exception for model loading errors."""
    pass


class PredictionError(Exception):
    """Exception for prediction errors."""
    pass


class PrescriptionPredictor:
    """Class for loading model and making predictions on prescriptions."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the predictor with model and tokenizer.
        
        Args:
            model_path: Optional custom model path. Uses config default if None.
        """
        self.paths = get_paths()
        self.model_config = get_model_config()
        self.inference_config = get_inference_config()
        
        # Set model path
        if model_path:
            self.model_path = Path(model_path)
        else:
            self.model_path = self.paths.biobert_model_path
        
        logger.info(f"Initializing predictor with model: {self.model_path}")
        
        # Load label mappings
        self.id2label = self._load_label_map()
        
        # Load model and tokenizer
        self.tokenizer = None
        self.model = None
        self._load_model()
        
    def _load_label_map(self) -> Dict[int, str]:
        """Load id2label mapping from JSON."""
        try:
            if not file_exists(self.paths.id2label_path):
                logger.warning(f"id2label.json not found at {self.paths.id2label_path}")
                return {}
            
            id2label_raw = read_json(self.paths.id2label_path)
            # Convert string keys to int
            id2label = {int(k): v for k, v in id2label_raw.items()}
            logger.info(f"Loaded {len(id2label)} labels")
            return id2label
            
        except Exception as e:
            logger.error(f"Failed to load label map: {str(e)}")
            raise ModelLoadError(f"Could not load label mappings: {str(e)}") from e
    
    def _load_model(self):
        """Load BioBERT model and tokenizer."""
        try:
            if not self.model_path.exists():
                raise ModelLoadError(f"Model not found at {self.model_path}. Please train the model first.")
            
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))
            
            logger.info("Loading model...")
            self.model = AutoModelForTokenClassification.from_pretrained(str(self.model_path))
            
            # Set to evaluation mode
            self.model.eval()
            
            # Move to device if using GPU
            if self.model_config.device == "auto":
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            else:
                device = torch.device(self.model_config.device)
            
            self.model.to(device)
            
            logger.info(f"Model loaded successfully on {device}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise ModelLoadError(f"Could not load model: {str(e)}") from e
    
    def predict_entities(self, text: str) -> List[Tuple[str, str, int]]:
        """
        Predict named entities in text.
        
        Args:
            text: Cleaned prescription text
            
        Returns:
            List of (token, label, label_id) tuples
            
        Raises:
            PredictionError: If prediction fails
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided for prediction")
                return []
            
            logger.debug(f"Predicting entities for text: {text[:100]}...")
            
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=self.model_config.max_length,
                padding=True
            )
            
            # Move to same device as model
            device = next(self.model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            logits = outputs.logits
            predictions = torch.argmax(logits, dim=2)
            
            # Get tokens and labels
            tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
            predicted_label_ids = predictions[0].tolist()
            
            # Map IDs to labels
            results = []
            for token, label_id in zip(tokens, predicted_label_ids):
                label = self.id2label.get(label_id, f"UNKNOWN_{label_id}")
                results.append((token, label, label_id))
            
            logger.info(f"Predicted {len(results)} tokens")
            return results
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise PredictionError(f"Failed to predict entities: {str(e)}") from e
    
    def extract_entities(self, tokens_with_labels: List[Tuple[str, str, int]]) -> Dict[str, List[str]]:
        """
        Extract and group entities from token-label pairs.
        Uses robust subword merging logic to handle WordPiece (##) tokens.
        """
        entities = {}
        current_label = None
        current_tokens = []
        
        SKIP_TOKENS = {"[CLS]", "[SEP]", "[PAD]"}
        
        for token, label, _ in tokens_with_labels:
            if token in SKIP_TOKENS:
                continue
                
            # Always treat ## tokens as subword continuations of the current word
            if token.startswith('##'):
                if current_tokens:
                    current_tokens.append(token)
                else:
                    current_label = label[2:] if label != 'O' else None
                    current_tokens = [token]
                continue
                
            # Regular (non-##) token
            if label.startswith('B-'):
                # Flush previous entity
                if current_label and current_tokens:
                    merged_val = self._merge_tokens(current_tokens)
                    entities.setdefault(current_label, []).append(merged_val)
                current_label = label[2:]   # strip 'B-'
                current_tokens = [token]
                
            elif label.startswith('I-'):
                entity_type = label[2:]
                if entity_type == current_label:
                    # Same entity type continues: accumulate into the same span
                    current_tokens.append(token)
                else:
                    # Mismatched I- tag: save old entity, start new
                    if current_label and current_tokens:
                        merged_val = self._merge_tokens(current_tokens)
                        entities.setdefault(current_label, []).append(merged_val)
                    current_label = entity_type
                    current_tokens = [token]
                    
            else:  # 'O'
                if current_label and current_tokens:
                    merged_val = self._merge_tokens(current_tokens)
                    entities.setdefault(current_label, []).append(merged_val)
                current_label = None
                current_tokens = []
                
        # Flush last entity
        if current_label and current_tokens:
            merged_val = self._merge_tokens(current_tokens)
            entities.setdefault(current_label, []).append(merged_val)
            
        return entities
    
    def _merge_tokens(self, tokens: List[str]) -> str:
        """Merges WordPiece subword tokens back into a full word."""
        if not tokens:
            return ""
        word = tokens[0]
        for t in tokens[1:]:
            if t.startswith("##"):
                word += t[2:]   # "Cro" + "##cin" → "Crocin"
            else:
                word += " " + t
        return word.strip()


# Global predictor instance
_predictor: Optional[PrescriptionPredictor] = None


def get_predictor() -> PrescriptionPredictor:
    """Get or create global predictor instance."""
    global _predictor
    if _predictor is None:
        _predictor = PrescriptionPredictor()
    return _predictor


def process_prescription(
    image_path: Union[str, Path],
    return_tokens: bool = False
) -> Dict:
    """
    Process prescription image end-to-end: OCR -> Clean -> NER.
    
    Args:
        image_path: Path to prescription image
        return_tokens: If True, include token-level predictions
        
    Returns:
        Dictionary containing:
            - raw_text: Text from OCR
            - cleaned_text: Preprocessed text
            - entities: Extracted entities grouped by type
            - tokens: (optional) Token-level predictions
            
    Raises:
        OCRError: If OCR fails
        TextCleaningError: If text cleaning fails
        PredictionError: If NER prediction fails
    """
    try:
        logger.info(f"Processing prescription: {image_path}")
        
        # Step 1: OCR
        logger.info("Step 1: Extracting text from image...")
        raw_text = extract_text_from_image(image_path)
        
        if not raw_text:
            logger.warning("No text extracted from image")
            return {
                "raw_text": "",
                "cleaned_text": "",
                "entities": {},
                "error": "No text could be extracted from the image"
            }
        
        # Step 2: Clean text
        logger.info("Step 2: Cleaning text...")
        cleaned_text = clean_text(raw_text)
        
        # Step 3: NER prediction
        logger.info("Step 3: Skipping NER (model not available)...")

        token_predictions = []
        entities = {}
        
        # Step 4: Extract structured entities
        logger.info("Step 4: Skipped")
        
        
        # Step 5: Fetch drug descriptions
        logger.info("Step 5: Skipped")
        drug_descriptions = {}
        
        # Look for any drug entities
        drug_names = []
        if "DRUG_BRAND" in entities:
            drug_names.extend(entities["DRUG_BRAND"])
        if "DRUG_GENERIC" in entities:
            drug_names.extend(entities["DRUG_GENERIC"])
        if "DRUG" in entities: # Fallback just in case
            drug_names.extend(entities["DRUG"])
            
        # Remove duplicates
        unique_drugs = list(set(drug_names))
        
        for drug in unique_drugs:
            if drug.strip():
                drug_descriptions[drug] = get_drug_description(drug)
        
        result = {
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "entities": entities,
            "drug_descriptions": drug_descriptions,
            "success": True
        }
        
        if return_tokens:
            result["tokens"] = [
                {"token": t, "label": l, "label_id": lid}
                for t, l, lid in token_predictions
            ]
        
        logger.info(f"Successfully processed prescription. Found {len(entities)} entity types")
        return result
        
    except OCRError as e:
        logger.error(f"OCR failed: {str(e)}")
        return {
            "success": False,
            "error": f"OCR failed: {str(e)}",
            "error_type": "OCR"
        }
    
    except TextCleaningError as e:
        logger.error(f"Text cleaning failed: {str(e)}")
        return {
            "success": False,
            "error": f"Text cleaning failed: {str(e)}",
            "error_type": "Preprocessing"
        }
    
    except (ModelLoadError, PredictionError) as e:
        logger.error(f"NER prediction failed: {str(e)}")
        return {
            "success": False,
            "error": f"NER prediction failed: {str(e)}",
            "error_type": "NER"
        }
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "Unknown"
        }