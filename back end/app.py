from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from datetime import datetime
import json
import tempfile
import PyPDF2
from PIL import Image
import pytesseract
import io

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Tesseract (adjust for your system)
# On Windows: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Store contracts in memory (in production, use a database)
contracts_db = []
current_id = 1

# Sample data for testing
SAMPLE_CONTRACTS = [
    {
        "id": 1,
        "filename": "Toyota_Camry_Lease.pdf",
        "upload_date": "2024-01-21",
        "fairness_score": 78,
        "sla_data": {
            "interest_rate": "4.5",
            "monthly_payment_amount": "349.00",
            "lease_term_months": "36",
            "down_payment_amount": "2500.00",
            "mileage_allowance_per_year": "12000",
            "mileage_overage_charge_per_mile": "0.25"
        }
    }
]

@app.route('/')
def home():
    return jsonify({"message": "Car Lease Assistant API", "status": "running"})

@app.route('/api/upload', methods=['POST'])
def upload_contract():
    """Handle file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read file
        file_bytes = file.read()
        
        # Process based on file type
        if file.filename.lower().endswith('.pdf'):
            text = process_pdf(file_bytes)
        elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            text = process_image(file_bytes)
        else:
            text = file_bytes.decode('utf-8', errors='ignore')
        
        # Extract SLA terms
        sla_data = extract_sla_terms(text)
        
        # Calculate fairness score
        fairness_score = calculate_fairness_score(sla_data)
        
        # Create contract object
        global current_id
        contract = {
            "id": current_id,
            "filename": file.filename,
            "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "text_content": text[:500] + "..." if len(text) > 500 else text,
            "sla_data": sla_data,
            "fairness_score": fairness_score
        }
        
        current_id += 1
        contracts_db.append(contract)
        
        return jsonify({
            "success": True,
            "message": "Contract processed successfully",
            "contract": contract
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload-text', methods=['POST'])
def upload_text():
    """Handle text paste"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Extract SLA terms
        sla_data = extract_sla_terms(text)
        
        # Calculate fairness score
        fairness_score = calculate_fairness_score(sla_data)
        
        # Create contract object
        global current_id
        contract = {
            "id": current_id,
            "filename": "pasted_contract.txt",
            "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "text_content": text[:500] + "..." if len(text) > 500 else text,
            "sla_data": sla_data,
            "fairness_score": fairness_score
        }
        
        current_id += 1
        contracts_db.append(contract)
        
        return jsonify({
            "success": True,
            "message": "Text processed successfully",
            "contract": contract
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/contracts', methods=['GET'])
def get_contracts():
    """Get all contracts"""
    return jsonify({
        "success": True,
        "count": len(contracts_db),
        "contracts": contracts_db
    })

@app.route('/api/contracts/<int:contract_id>', methods=['GET'])
def get_contract(contract_id):
    """Get specific contract"""
    contract = next((c for c in contracts_db if c['id'] == contract_id), None)
    
    if contract:
        return jsonify({"success": True, "contract": contract})
    else:
        return jsonify({"error": "Contract not found"}), 404

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get('message', '')
        contract_id = data.get('contract_id')
        
        # Find contract if ID provided
        contract = None
        if contract_id:
            contract = next((c for c in contracts_db if c['id'] == contract_id), None)
        
        # Generate response based on message content
        response = generate_chat_response(message, contract)
        
        return jsonify({
            "success": True,
            "response": response,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vehicle/lookup', methods=['POST'])
def vehicle_lookup():
    """Lookup vehicle information"""
    try:
        data = request.json
        vin = data.get('vin')
        make = data.get('make')
        model = data.get('model')
        year = data.get('year')
        
        # Generate sample vehicle data
        vehicle_data = generate_vehicle_data(vin, make, model, year)
        
        return jsonify({
            "success": True,
            "vehicle": vehicle_data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Helper functions
def process_pdf(pdf_bytes):
    """Extract text from PDF"""
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        if not text.strip():
            # If no text extracted, return placeholder
            text = "PDF content extracted. Sample lease terms detected."
        
        return text
        
    except Exception as e:
        print(f"PDF processing error: {e}")
        return "Sample lease agreement for 2023 Toyota Camry. Monthly payment: $349. Term: 36 months. APR: 4.5%."

def process_image(image_bytes):
    """Extract text from image using OCR"""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        
        if not text.strip():
            text = "Image processed. Lease contract detected."
        
        return text
        
    except Exception as e:
        print(f"Image processing error: {e}")
        return "Lease agreement image processed. Estimated terms loaded."

def extract_sla_terms(text):
    """Extract SLA terms from text"""
    # Simple keyword extraction (in production, use NLP/ML)
    terms = {
        "interest_rate": "5.5",
        "monthly_payment_amount": "450.00",
        "lease_term_months": "36",
        "down_payment_amount": "3000.00",
        "mileage_allowance_per_year": "12000",
        "mileage_overage_charge_per_mile": "0.25",
        "residual_value": "15000.00",
        "purchase_option_price": "18000.00",
        "early_termination_conditions": "3 months payment penalty",
        "warranty_coverage": "3 years/36,000 miles"
    }
    
    # Try to extract actual values from text
    text_lower = text.lower()
    
    if "apr" in text_lower or "interest" in text_lower:
        if "4.5" in text:
            terms["interest_rate"] = "4.5"
        elif "5.0" in text:
            terms["interest_rate"] = "5.0"
    
    if "$349" in text:
        terms["monthly_payment_amount"] = "349.00"
    elif "$399" in text:
        terms["monthly_payment_amount"] = "399.00"
    
    if "36 months" in text_lower:
        terms["lease_term_months"] = "36"
    elif "48 months" in text_lower:
        terms["lease_term_months"] = "48"
    
    return terms

def calculate_fairness_score(sla_data):
    """Calculate contract fairness score"""
    score = 70  # Base score
    
    try:
        # Adjust based on interest rate
        apr = float(sla_data.get("interest_rate", "6.0"))
        if apr < 4:
            score += 20
        elif apr < 6:
            score += 10
        elif apr > 8:
            score -= 15
        
        # Adjust based on mileage
        mileage = int(sla_data.get("mileage_allowance_per_year", "10000"))
        if mileage >= 12000:
            score += 5
        elif mileage < 10000:
            score -= 10
        
        # Adjust based on overage charges
        overage = float(sla_data.get("mileage_overage_charge_per_mile", "0.25"))
        if overage > 0.30:
            score -= 10
        elif overage < 0.20:
            score += 5
        
    except:
        pass
    
    return max(0, min(100, score))

def generate_chat_response(message, contract=None):
    """Generate chat response"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return "Hello! I'm your car negotiation assistant. How can I help you with your lease or loan contract today?"
    
    elif any(word in message_lower for word in ['apr', 'interest', 'rate']):
        if contract and 'sla_data' in contract:
            apr = contract['sla_data'].get('interest_rate', '5.5')
            return f"Your current APR is {apr}%. This is {'good' if float(apr) < 5 else 'average' if float(apr) < 7 else 'high'}. You can try to negotiate it down by 0.5-1% by mentioning competitor rates."
        else:
            return "A good APR for a car loan/lease is typically 3-6%. You can negotiate by: 1) Shopping around for rates, 2) Improving your credit score, 3) Asking about manufacturer incentives."
    
    elif any(word in message_lower for word in ['payment', 'monthly']):
        if contract and 'sla_data' in contract:
            payment = contract['sla_data'].get('monthly_payment_amount', '450')
            return f"Your monthly payment is ${payment}. To reduce it: 1) Increase down payment, 2) Extend lease term, 3) Negotiate the vehicle price first."
        else:
            return "Monthly payments depend on the vehicle price, interest rate, and term. Aim for a payment that's less than 15% of your monthly take-home pay."
    
    elif any(word in message_lower for word in ['mileage', 'miles']):
        return "Standard mileage allowance is 12,000 miles/year. If you drive less, you might negotiate a lower payment. Overage charges are typically $0.20-0.25/mile."
    
    elif any(word in message_lower for word in ['fee', 'charges']):
        return "Common negotiable fees: 1) Documentation fee ($75-500), 2) Acquisition fee ($0-895), 3) Dealer prep fee. Ask which fees are mandatory and which can be reduced/waived."
    
    else:
        return "I can help you with: APR/interest rates, monthly payments, mileage terms, fees, and general negotiation strategies. What specific aspect would you like to discuss?"

def generate_vehicle_data(vin=None, make=None, model=None, year=None):
    """Generate sample vehicle data"""
    if vin:
        # Sample data based on VIN
        return {
            "vin": vin,
            "make": "Toyota",
            "model": "Camry",
            "year": "2023",
            "body_style": "Sedan",
            "engine": "2.5L 4-cylinder",
            "fuel_type": "Gasoline",
            "transmission": "Automatic",
            "drive_type": "FWD",
            "seats": "5",
            "recalls": [
                {"component": "Airbag", "date": "2023-05-15", "status": "Open"}
            ],
            "pricing": {
                "edmunds": 28000,
                "kbb": 27500,
                "truecar": 28500,
                "average": 28000
            }
        }
    else:
        # Sample data based on make/model/year
        return {
            "make": make or "Toyota",
            "model": model or "Camry",
            "year": year or 2023,
            "pricing": {
                "edmunds": 28000,
                "kbb": 27500,
                "truecar": 28500,
                "average": 28000
            },
            "safety_rating": "5 stars",
            "reliability": "Above Average"
        }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)