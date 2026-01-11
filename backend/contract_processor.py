import pdfplumber
import PyPDF2
from docx import Document
import re
from typing import Dict, List
import json

class ContractProcessor:
    def __init__(self):
        self.key_terms = [
            "interest rate", "apr", "annual percentage rate",
            "lease term", "contract term", "duration",
            "monthly payment", "monthly lease payment",
            "down payment", "security deposit",
            "residual value", "purchase option",
            "mileage allowance", "mileage limit",
            "excess mileage", "overage charge",
            "early termination", "early payoff",
            "maintenance", "warranty",
            "insurance", "gap insurance",
            "penalty", "late fee", "default"
        ]
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF files"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except:
            # Fallback to PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        return text
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX files"""
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    
    def find_key_terms(self, text: str) -> Dict[str, List[str]]:
        """Find key terms in contract text"""
        results = {}
        text_lower = text.lower()
        
        for term in self.key_terms:
            pattern = r'([$]?\d+[.,]?\d*[%]?\s*(?:per\s*(?:year|month)?)?\s*(?:to\s*)?[$]?\d*[.,]?\d*[%]?)'
            matches = re.findall(f"{term}.*?{pattern}", text_lower, re.DOTALL)
            if matches:
                results[term] = matches[:3]  # Get up to 3 matches
        
        return results
    
    def extract_financial_terms(self, text: str) -> Dict:
        """Extract financial terms using regex patterns"""
        patterns = {
            "apr": r'APR\s*[:=]?\s*([\d.]+)%',
            "monthly_payment": r'monthly\s*(?:payment|lease)\s*[:=]?\s*[$]?\s*([\d,]+(?:\.\d{2})?)',
            "down_payment": r'down\s*(?:payment|deposit)\s*[:=]?\s*[$]?\s*([\d,]+(?:\.\d{2})?)',
            "lease_term": r'lease\s*term\s*[:=]?\s*(\d+)\s*(?:months|years)',
            "mileage_limit": r'mileage\s*(?:limit|allowance)\s*[:=]?\s*(\d+,\d+|\d+)\s*miles',
            "residual_value": r'residual\s*value\s*[:=]?\s*[$]?\s*([\d,]+(?:\.\d{2})?)',
        }
        
        extracted = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted[key] = match.group(1)
        
        return extracted