import wikipedia
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CACHE_FILE = Path(__file__).parent.parent.parent / "models" / "drug_cache.json"

def _load_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_cache(cache):
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)
    except Exception as e:
        logger.warning(f"Failed to save drug cache: {e}")

_drug_cache = _load_cache()

def get_drug_description(drug_name: str) -> dict:
    """
    Fetches a description using Wikipedia API, prioritizing medication pages.
    Returns: {"root_name": str, "description": str}
    """
    if not drug_name or len(drug_name.strip()) < 3:
        return {"root_name": drug_name, "description": "No description available."}
        
    drug_name_clean = drug_name.strip().lower()
    
    if drug_name_clean in _drug_cache:
        return _drug_cache[drug_name_clean]
        
    try:
        # Step 1: Search Wikipedia prioritizing medical context
        # This prevents "Delcon" from returning "US Postal Service Delivery Confirmation"
        search_results = wikipedia.search(f"{drug_name_clean} medication OR drug OR syrup")
        if not search_results:
            # Fallback to plain search
            search_results = wikipedia.search(drug_name_clean)
            
        if not search_results:
            result = {"root_name": drug_name.title(), "description": "No Wikipedia description found."}
            _drug_cache[drug_name_clean] = result
            _save_cache(_drug_cache)
            return result
            
        # Try getting summary for the topmost result
        page_title = search_results[0]
        # Get 2 sentences to keep it brief
        summary = wikipedia.summary(page_title, sentences=2, auto_suggest=False)
        
        # We couldn't fetch a generic root reliably, so we use the brand name capitalized
        result = {"root_name": drug_name.title(), "description": summary}
        _drug_cache[drug_name_clean] = result
        _save_cache(_drug_cache)
        return result
        
    except wikipedia.exceptions.DisambiguationError as e:
        # If ambiguous, grab the first option's summary safely
        try:
            summary = wikipedia.summary(e.options[0], sentences=2, auto_suggest=False)
            result = {"root_name": drug_name.title(), "description": summary}
            _drug_cache[drug_name_clean] = result
            _save_cache(_drug_cache)
            return result
        except Exception:
            return {"root_name": drug_name.title(), "description": "No description found (ambiguous term)."}
            
    except Exception as e:
        logger.warning(f"Failed to fetch wiki description for {drug_name}: {e}")
        return {"root_name": drug_name.title(), "description": "Description unavailable at this time."}
