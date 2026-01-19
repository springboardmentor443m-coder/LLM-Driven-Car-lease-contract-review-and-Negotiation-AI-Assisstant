import tempfile, os
import pdfplumber

def extract_text_from_pdf(pdf_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        path = tmp.name

    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"

    os.remove(path)

    if not text.strip():
        raise ValueError("Scanned PDF – OCR not enabled")

    return text
