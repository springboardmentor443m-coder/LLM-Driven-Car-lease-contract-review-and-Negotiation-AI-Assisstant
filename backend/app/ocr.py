import fitz  # PyMuPDF

def pdf_bytes_to_text(data: bytes) -> str:
    text = ""
    try:
        pdf = fitz.open(stream=data, filetype="pdf")
        for page in pdf:
            text += page.get_text()
    except Exception:
        return ""
    return text.strip()
