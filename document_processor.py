import pytesseract
from PIL import Image
import PyPDF2
import io
import pdf2image
import tempfile
import os

class OCRProcessor:
    def __init__(self):
        # Configure Tesseract path (adjust for your system)
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
    def process_document(self, file):
        """Process PDF or image file to extract text"""
        filename = file.filename.lower()
        
        if filename.endswith('.pdf'):
            return self._process_pdf(file)
        elif filename.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
            return self._process_image(file)
        else:
            raise ValueError("Unsupported file format")
    
    def _process_pdf(self, file):
        """Extract text from PDF"""
        text = ""
        
        try:
            # First try direct text extraction
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text.strip():
                    text += page_text + "\n"
            
            # If no text found, use OCR
            if not text.strip():
                text = self._ocr_pdf(file)
                
        except Exception as e:
            # Fallback to OCR
            text = self._ocr_pdf(file)
            
        return text
    
    def _ocr_pdf(self, file):
        """Use OCR on PDF pages"""
        file.seek(0)
        text = ""
        
        # Convert PDF to images
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(file.read())
            tmp_path = tmp_file.name
        
        try:
            images = pdf2image.convert_from_path(tmp_path)
            for image in images:
                page_text = pytesseract.image_to_string(image)
                text += page_text + "\n"
        finally:
            os.unlink(tmp_path)
            
        return text
    
    def _process_image(self, file):
        """Extract text from image"""
        image = Image.open(io.BytesIO(file.read()))
        text = pytesseract.image_to_string(image)
        return text