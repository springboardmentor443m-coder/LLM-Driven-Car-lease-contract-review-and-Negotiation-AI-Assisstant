from PIL import Image
import pytesseract
import fitz
import io
import os
from app.state import state

def image_ocr(file, tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    state.raw_text = pytesseract.image_to_string(Image.open(file))

def pdf_ocr(file, tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    state.raw_text = ""
    temp = "temp.pdf"

    with open(temp, "wb") as f:
        f.write(file.read())

    pdf = fitz.open(temp)
    for page in pdf:
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        state.raw_text += pytesseract.image_to_string(img)

    pdf.close()
    os.remove(temp)
