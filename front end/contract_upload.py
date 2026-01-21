import streamlit as st
from datetime import datetime
import pandas as pd
import sys
from pathlib import Path

# Fix imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

try:
    from utils import APIClient, OCRProcessor
except ImportError:
    # Create mock classes for development
    class APIClient:
        def __init__(self):
            pass
        
        def extract_sla(self, text):
            return {
                'interest_rate': '5.5',
                'monthly_payment_amount': '450',
                'lease_term_months': '36'
            }
    
    class OCRProcessor:
        def __init__(self):
            pass
        
        def process_pdf(self, pdf_bytes):
            return "Sample extracted text from PDF"
        
        def process_image(self, image_bytes):
            return "Sample extracted text from image"

# [Rest of the contract_upload.py code...]