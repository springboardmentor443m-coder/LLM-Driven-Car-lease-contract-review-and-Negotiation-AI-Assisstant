import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

from .vin_service import get_vehicle_details 
from .market_service import estimate_market_price

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)
MODEL_NAME = "llama-3.3-70b-versatile"

def clean_json_string(text: str):
    cleaned = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
    cleaned = re.sub(r"^```\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
    return cleaned.strip()

def fix_common_vin_errors(vin: str) -> str:
    """
    Fixes common OCR mistakes in VINs.
    """
    vin = vin.upper()
    if vin.startswith("4FA"):
        print(f"🔧 Auto-Correcting VIN: {vin} -> 1FA...")
        return "1" + vin[1:]
    if vin[0] in ['I', 'L']:
        return "1" + vin[1:]
    return vin

async def analyze_lease(text: str):
    
    # --- 1. SMART VIN SEARCH ---
    vin_match = re.search(r'[A-HJ-NPR-Z0-9]{17}', text)
    
    nhtsa_raw_data = {}
    market_raw_data = {"status": "Not Checked"}
    market_price = None
    
    vehicle_context = "NHTSA Data: Not Verified (VIN not found in text scan)."
    market_context = "Market Value: Not Available."
    
    if vin_match:
        raw_vin = vin_match.group(0)
        vin = fix_common_vin_errors(raw_vin)
        
        print(f"✅ Extracted VIN: {vin}")
        
        # Always add VIN to nhtsa_raw_data
        nhtsa_raw_data["VIN"] = vin
        
        details = await get_vehicle_details(vin)
        
        if details:
            # FIX: Mapping keys exactly as the frontend expects them
            nhtsa_raw_data = {
                "Make": details.get('Make'),
                "Model": details.get('Model'),
                "Model Year": details.get('Model Year'),
                "VIN": vin,
                "Engine": details.get('Engine HP', 'N/A')
            }
            
            make = nhtsa_raw_data['Make']
            model = nhtsa_raw_data['Model']
            year = nhtsa_raw_data['Model Year']
            
            vehicle_context = (
                f"*** OFFICIAL GOV DATA (NHTSA) ***\n"
                f"VIN: {vin}\n"
                f"Year: {year}\n"
                f"Make: {make}\n"
                f"Model: {model}\n"
                f"Engine: {nhtsa_raw_data['Engine']} HP\n"
            )
            
            if make and model and year:
                # Calculate Market Price
                market_price = estimate_market_price(make, model, year)
                
                if market_price:
                    market_raw_data = {
                        "estimated_price": market_price,
                        "currency": "USD",
                        "source": "RapidAPI / Algorithmic"
                    }
                    market_context = f"*** REAL MARKET VALUE ***: ${market_price:,.2f}"

    # --- 2. UPDATED PROMPT ---
    prompt = f"""
    You are an expert Senior Legal Contract Auditor for Auto Sales & Leases.
    I will provide the contract text below. You must extract data with extreme precision.

    DATA SOURCE A (CONTRACT TEXT):
    {text[:45000]}

    DATA SOURCE B (VEHICLE CONTEXT):
    {vehicle_context}
    {market_context}

    ---
    **YOUR INSTRUCTIONS:**

    1. **EXECUTIVE SUMMARY (Required length: 7-8 lines):**
        - Provide a comprehensive paragraph summary.
        - Mention the Parties and Vehicle details.
        - Clearly separate "Due at Signing" from "Monthly Payment".

    2. **FAIRNESS & RED FLAGS (Crucial):**
        - Compare the Contract Price/Payments against the {market_context}.
        - **Score Explanation:** Write exactly 2 sentences justifying the score using professional auditor vocabulary.
        - **Flags:** Identify 'Usurious Rent Charges', 'Arbitrary Addendum Items', or 'Capitalization Deficits'.

    **OUTPUT FORMAT (Return ONLY raw JSON, no markdown):**
    {{
      "executive_summary": "Insert your detailed 7-8 line summary here...",
      
      "sla_extraction": {{
        "interest_rate_apr": "Extract APR or Money Factor",
        "lease_term_months": "Extract duration",
        "monthly_payment": "Extract total monthly payment",
        "down_payment": "Extract Down Payment/Cap Cost Reduction",
        "residual_value": "Extract Purchase Option/Residual",
        "mileage_allowance_per_year": "Extract mileage limit",
        "excess_mileage_fee": "Extract excess mile fee",
        "buyout_price": "Extract buyout price",
        "early_termination_fee": "Extract early termination fee",
        "warranty_coverage": "Extract warranty terms",
        "maintenance_responsibilities": "Extract maintenance terms",
        "penalties_late_fees": "Extract late fee"
      }},

      "negotiation_target": {{
        "current_monthly": "Value from text",
        "target_monthly": "Calculate a fair offer (approx 10-15% less)",
        "market_comparison": "Compare Contract Price vs Market Price",
        "reasoning": "Explain why the target price is fair."
      }},

      "fairness_analysis": {{
        "score": 0,
        "score_explanation": "Justify the score using professional auditor prose.",
        "flags": ["List specific red flags using senior auditor terminology..."]
      }}
    }}
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        llm_result = json.loads(clean_json_string(response.choices[0].message.content))
        
        # Merge external data back in for the frontend
        llm_result["nhtsa_details"] = nhtsa_raw_data
        llm_result["rapidapi_details"] = market_raw_data
        
        # Ensure fairness score math is applied correctly to the final object
        if market_price:
            # Simple math for the internal score if the LLM didn't calculate it well
            extracted_payment = float(str(llm_result["sla_extraction"].get("monthly_payment", "0")).replace("$","").replace(",",""))
            if extracted_payment > (market_price * 0.015):
                llm_result["fairness_analysis"]["score"] = 65 # Example penalty
        
        return llm_result

    except Exception as e:
        print(f"LLM Analysis Failed: {e}")
        return {"error": str(e)}

async def chat_negotiation(history: list, user_message: str):
    if not client:
        return "⚠️ Error: AI Client not initialized (Check API Key)."

    messages = []
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})
        
    if messages[-1]['content'] != user_message:
         messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return "I'm having trouble connecting to the brain right now. Please try again."