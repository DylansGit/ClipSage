# ocr.py

import pytesseract
import os
from PIL import Image

# Optional: allow override via environment variable
custom_path = os.getenv("TESSERACT_PATH")

if custom_path:
    pytesseract.pytesseract.tesseract_cmd = custom_path
    print(f"[OCR] Using custom Tesseract path: {custom_path}")
else:
    print("[OCR] Using system Tesseract (must be in PATH)")

def extract_text_from_image(image: Image.Image) -> str:
    """
    Extracts text from an image using Tesseract OCR.
    """
    try:
        rgb_image = image.convert("RGB")
        text = pytesseract.image_to_string(rgb_image)
        return text.strip()
    except Exception as e:
        print(f"[OCR] Failed to extract text: {e}")
        return ""
