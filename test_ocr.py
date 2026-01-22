import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

img = Image.open("page_0.png")  # from previous step

text = pytesseract.image_to_string(img, lang="eng")
print(text)