import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SARVAM_API_KEY")

SARVAM_URL = "https://api.sarvam.ai/v1/vision"  # confirm exact endpoint from docs


def extract_text_from_image(image_path):
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    files = {
        "file": open(image_path, "rb")
    }

    response = requests.post(
        SARVAM_URL,
        headers=headers,
        files=files
    )

    if response.status_code != 200:
        raise Exception(f"OCR failed: {response.text}")

    result = response.json()

    # Adjust according to Sarvam API response format
    extracted_text = result.get("text", "")

    return extracted_text