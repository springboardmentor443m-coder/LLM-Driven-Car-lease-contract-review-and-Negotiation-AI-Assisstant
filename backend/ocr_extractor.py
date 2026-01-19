import pytesseract
from PIL import Image
import pdfplumber
import re
import os

def extract_text(file_path):
    text = ""

    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

    else:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)

    return text


def extract_vin(text):
    # VIN = 17 characters (letters + numbers, excluding I,O,Q)
    pattern = r"\b[A-HJ-NPR-Z0-9]{17}\b"
    matches = re.findall(pattern, text)
    return matches[0] if matches else None
