"""
test_ner.py — Test your trained Bio_ClinicalBERT NER model on prescription text.

Place this file at the project root and run:
    python test_ner.py

Works locally (Windows) and on Google Colab without path changes.
"""

import sys
import json
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForTokenClassification

# ── Paths ────────────────────────────────────────────────────────────────────
# Using __file__ makes this work on both Windows (locally) and Colab
PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH   = PROJECT_ROOT / "models" / "biobert_prescription"

# ── Label map is read directly from the saved model's config ─────────────────
# Do NOT hardcode this — it must always match what the model was trained with.

# ── Load model ────────────────────────────────────────────────────────────────
def load_model():
    if not MODEL_PATH.exists():
        print(f"\n❌ ERROR: Trained model not found at:\n   {MODEL_PATH}")
        print("\n👉 You need to train first:")
        print("   python retrain.py")
        print("   (or download from Colab and place in models/biobert_prescription/)\n")
        sys.exit(1)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"📂 Loading model from: {MODEL_PATH}")
    print(f"🖥️  Inference device  : {device}")
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))
    model     = AutoModelForTokenClassification.from_pretrained(str(MODEL_PATH))
    model.to(device)
    model.eval()

    # Read id2label directly from the model config — always in sync with training
    id2label = {int(k): v for k, v in model.config.id2label.items()}
    print(f"✅ Model loaded with {len(id2label)} labels: {id2label}\n")
    return tokenizer, model, id2label, device


# ── Predict tokens ────────────────────────────────────────────────────────────
def predict_tokens(text, tokenizer, model, id2label, device):
    """Returns list of (token, label) pairs for each token in text."""
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=256,
        padding=True
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    predictions   = torch.argmax(outputs.logits, dim=2)[0].tolist()
    tokens        = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

    results = []
    for token, pred_id in zip(tokens, predictions):
        label = id2label.get(pred_id, "O")
        results.append((token, label))

    return results


# ── Merge subwords & group entities ──────────────────────────────────────────
def extract_entities(token_label_pairs):
    """
    Merges WordPiece subwords (##) and groups tokens into entities.

    Key rule: a ## token is ALWAYS a continuation of the current word,
    regardless of whether the model gave it a B- or I- label. This prevents
    single words like 'Crocin' from being split into multiple entity spans.

    Example:
      ('Cro', B-DRUG_BRAND), ('##cin', B-DRUG_BRAND) -> DRUG_BRAND: 'Crocin'
    """
    entities       = {}
    current_label  = None
    current_tokens = []

    SKIP_TOKENS = {"[CLS]", "[SEP]", "[PAD]"}

    for token, label in token_label_pairs:
        if token in SKIP_TOKENS:
            continue

        # Always treat ## tokens as subword continuations of the current word
        if token.startswith('##'):
            if current_tokens:
                current_tokens.append(token)
            else:
                current_label  = label[2:] if label != 'O' else None
                current_tokens = [token]
            continue

        # Regular (non-##) token
        if label.startswith('B-'):
            # Flush previous entity
            if current_label and current_tokens:
                entities.setdefault(current_label, []).append(_merge(current_tokens))
            current_label  = label[2:]   # strip 'B-'
            current_tokens = [token]

        elif label.startswith('I-'):
            entity_type = label[2:]
            if entity_type == current_label:
                # Same entity type continues: accumulate into the same span
                current_tokens.append(token)
            else:
                # Mismatched I- tag: save old entity, start new
                if current_label and current_tokens:
                    entities.setdefault(current_label, []).append(_merge(current_tokens))
                current_label  = entity_type
                current_tokens = [token]

        else:  # 'O'
            if current_label and current_tokens:
                entities.setdefault(current_label, []).append(_merge(current_tokens))
            current_label  = None
            current_tokens = []

    # Flush last entity
    if current_label and current_tokens:
        entities.setdefault(current_label, []).append(_merge(current_tokens))

    return entities


def _merge(tokens):
    """Merges WordPiece subword tokens back into a full word."""
    word = tokens[0]
    for t in tokens[1:]:
        if t.startswith("##"):
            word += t[2:]   # "Cro" + "##cin" → "Crocin"
        else:
            word += " " + t
    return word.strip()


# ── Pretty print ──────────────────────────────────────────────────────────────
def print_token_table(token_label_pairs):
    """Prints a neat token → label table."""
    print(f"{'TOKEN':<25} {'LABEL'}")
    print("-" * 45)
    for token, label in token_label_pairs:
        if token not in {"[CLS]", "[SEP]", "[PAD]"}:
            marker = "  ✦" if label != "O" else ""
            print(f"  {token:<23} {label}{marker}")
    print()


def print_entities(entities):
    """Prints structured entity output."""
    if not entities:
        print("  (no entities found — is the model trained yet?)\n")
        return
    for etype, values in entities.items():
        print(f"  {etype:<18} → {', '.join(values)}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    tokenizer, model, id2label, device = load_model()

    # ── Test cases ────────────────────────────────────────────────────────────
    test_sentences = [
        "Tab Crocin 500mg BD x 3 days",
        "Cap Dolo 650 TDS x 5 days",
        "Syp Augmentin 625mg BD AC x 7 days",
        "Tab Metformin 500mg OD PM x 30 days Cap Omez 20mg OD AM",
        "Inj Vitamin D3 60000 IU OD x 1 month",
    ]

    for i, text in enumerate(test_sentences, 1):
        print(f"{'='*55}")
        print(f"🧪 TEST {i}: {text}")
        print(f"{'='*55}\n")

        # Step 1: Token-level predictions
        token_labels = predict_tokens(text, tokenizer, model, id2label, device)

        print("📌 Token → Label:")
        print_token_table(token_labels)

        # Step 2: Extract structured entities
        entities = extract_entities(token_labels)

        print("📋 Structured Entities:")
        print_entities(entities)

        # Step 3: JSON output
        print("🗂️  JSON Output:")
        print(json.dumps(entities, indent=2))
        print()


if __name__ == "__main__":
    main()
