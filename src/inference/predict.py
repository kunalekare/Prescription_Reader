from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
import json
from src.ocr.sarvam_ocr import extract_text_from_image
from src.preprocessing.text_cleaner import clean_text

MODEL_PATH = "models/biobert_prescription"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)

model.eval()


def predict_entities(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    predictions = torch.argmax(logits, dim=2)

    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    predicted_labels = predictions[0].tolist()

    return list(zip(tokens, predicted_labels))


def process_prescription(image_path):
    print("Running OCR...")
    raw_text = extract_text_from_image(image_path)

    print("Cleaning text...")
    cleaned_text = clean_text(raw_text)

    print("Running BioBERT...")
    entities = predict_entities(cleaned_text)

    return {
        "raw_text": raw_text,
        "cleaned_text": cleaned_text,
        "entities": entities
    }