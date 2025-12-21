from pdf2image import convert_from_path
import pytesseract
import os

POPPLER_PATH = r"C:\Users\rajal\Downloads\release-25.12.0-0\poppler-25.12.0\Library\bin"

def extract_text_from_pdf(pdf_path, output_txt_path):
    pages = convert_from_path(
        pdf_path,
        dpi=300,
        poppler_path=POPPLER_PATH
    )

    extracted_text = ""

    for i, page in enumerate(pages):
        text = pytesseract.image_to_string(page)
        extracted_text += f"\n--- Page {i+1} ---\n{text}"

    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    return output_txt_path
