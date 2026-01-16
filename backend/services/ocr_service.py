import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io
import re

def clean_text(text: str) -> str:
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

async def extract_text_from_file(file_bytes: bytes, filename: str):
    full_text = ""
    try:
        if filename.lower().endswith('.pdf'):
            images = convert_from_bytes(file_bytes)
            for img in images:
                full_text += pytesseract.image_to_string(img) + "\n"
        else:
            image = Image.open(io.BytesIO(file_bytes))
            full_text = pytesseract.image_to_string(image)
            
        return {"text": clean_text(full_text)}
    except Exception as e:
        return {"error": str(e)}
        