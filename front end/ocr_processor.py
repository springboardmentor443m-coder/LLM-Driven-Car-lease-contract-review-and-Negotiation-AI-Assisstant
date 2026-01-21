import pytesseract
from PIL import Image
import PyPDF2
import io
import pdf2image
import tempfile
import os

# Remove import fitz if you don't have PyMuPDF installed
# Install it with: pip install PyMuPDF
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

class OCRProcessor:
    def __init__(self):
        # Configure Tesseract (adjust for your system)
        # On Windows, you might need: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        # On Linux/Mac: usually installed system-wide
        pass
    
    def process_pdf(self, pdf_bytes):
        """Extract text from PDF using multiple methods"""
        text = ""
        
        try:
            # Method 1: Try PyMuPDF for better PDF extraction if available
            if HAS_PYMUPDF:
                text = self._process_with_pymupdf(pdf_bytes)
            
            # Method 2: If no text found, use PyPDF2
            if not text.strip():
                text = self._process_with_pypdf2(pdf_bytes)
            
            # Method 3: If still no text, use OCR
            if not text.strip():
                text = self._process_with_ocr(pdf_bytes, is_pdf=True)
                
        except Exception as e:
            print(f"PDF processing error: {e}")
            # Fallback to OCR
            text = self._process_with_ocr(pdf_bytes, is_pdf=True)
        
        return text
    
    def process_image(self, image_bytes):
        """Extract text from image"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Image processing error: {e}")
            return ""
    
    def _process_with_pymupdf(self, pdf_bytes):
        """Extract text using PyMuPDF (fitz)"""
        text = ""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(pdf_bytes)
                tmp_path = tmp_file.name
            
            # Open with PyMuPDF
            doc = fitz.open(tmp_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
            
            doc.close()
            os.unlink(tmp_path)
            
        except Exception as e:
            print(f"PyMuPDF error: {e}")
        
        return text
    
    def _process_with_pypdf2(self, pdf_bytes):
        """Extract text using PyPDF2"""
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"PyPDF2 error: {e}")
        
        return text
    
    def _process_with_ocr(self, file_bytes, is_pdf=False):
        """Use OCR to extract text"""
        text = ""
        
        try:
            if is_pdf:
                # Convert PDF to images
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_file.write(file_bytes)
                    tmp_path = tmp_file.name
                
                try:
                    images = pdf2image.convert_from_path(tmp_path)
                    for image in images:
                        page_text = pytesseract.image_to_string(image)
                        text += page_text + "\n"
                finally:
                    os.unlink(tmp_path)
            else:
                # Process single image
                image = Image.open(io.BytesIO(file_bytes))
                text = pytesseract.image_to_string(image)
                
        except Exception as e:
            print(f"OCR error: {e}")
        
        return text