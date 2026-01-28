import pytesseract
from PIL import Image
import pdfplumber
import io


def extract_text(file):
    """
    Extract text from PDF or image file using OCR
    """

    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()

    
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text.strip()

    else:
        return "Unsupported file format"
