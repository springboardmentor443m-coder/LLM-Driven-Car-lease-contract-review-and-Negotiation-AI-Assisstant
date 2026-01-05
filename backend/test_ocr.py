import pytesseract
from PIL import Image

# IMPORTANT: Update this path if yours is different
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

print("Pillow + Tesseract imports OK!")
