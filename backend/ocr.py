import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_path
import os

# If tesseract path problem
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text(file_path):
    text = ""

    # ---------- PDF ----------
    if file_path.lower().endswith(".pdf"):
        # 1️⃣ Try normal text PDF
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        # 2️⃣ If scanned PDF → OCR
        if text.strip() == "":
            images = convert_from_path(file_path)
            for img in images:
                text += pytesseract.image_to_string(img)

    # ---------- IMAGE ----------
    else:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)

    return text