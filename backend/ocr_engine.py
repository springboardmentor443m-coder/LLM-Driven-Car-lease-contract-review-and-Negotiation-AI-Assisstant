import pytesseract
from PIL import Image
import pdfplumber
import os

# 🔹 MANUALLY SET TESSERACT PATH (CHANGE IF NEEDED)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text(file_path: str) -> str:
    """
    Extract text from PDF or image file
    """
    if file_path.lower().endswith(".pdf"):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    else:
        image = Image.open(file_path)
        return pytesseract.image_to_string(image)
