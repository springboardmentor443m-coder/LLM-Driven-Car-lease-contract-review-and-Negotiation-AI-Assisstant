import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

# Ensure these match your actual file names
from .vin_service import get_vehicle_details 
from .market_service import get_market_price

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
        
        details = await get_vehicle_details(vin)
        
        if details:
            nhtsa_raw_data = details 
            make = details.get('Make')
            model = details.get('Model')
            year = details.get('Model Year')
            
            vehicle_context = (
                f"*** OFFICIAL GOV DATA (NHTSA) ***\n"
                f"VIN: {vin}\n"
                f"Year: {year}\n"
                f"Make: {make}\n"
                f"Model: {model}\n"
                f"Engine: {details.get('Engine HP', 'N/A')} HP\n"
            )
            
            if make and model and year:
                # Calculate Market Price
                market_price = await get_market_price(make, model, year)
                
                if market_price:
                    market_raw_data = {
                        "estimated_price": market_price,
                        "currency": "USD",
                        "source": "RapidAPI / Algorithmic"
                    }
                    market_context = f"*** REAL MARKET VALUE ***: ${market_price:,.2f}"

    # --- 2. UPDATED PROMPT (THE FIX) ---
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
       - **Score Explanation:** Write exactly 2 sentences explaining WHY the deal is good/bad based on the math.
       - **Flags:** Look for "Doc Fee" > $500, "Nitrogen", "Window Etch", "Market Adjustment", or high interest rates.

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
        "score": 50,
        "score_explanation": "The dealer is charging $3,000 over market value. This indicates a high markup.",
        "flags": ["List specific red flags found..."]
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
        
        return llm_result

    except Exception as e:
        print(f"LLM Analysis Failed: {e}")
        return {"error": str(e)}

async def chat_negotiation(history: list, user_message: str):
    """
    Handles the chat conversation.
    The 'history' list ALREADY contains the System Prompt with the Contract Text 
    (sent from the Frontend).
    """
    # 1. Safety Check
    if not client:
        return "⚠️ Error: AI Client not initialized (Check API Key)."

    # 2. Format Messages for Groq/LLM
    # The Frontend sends a list of { "role": "...", "content": "..." }
    # We just need to pass this directly to the AI.
    messages = []
    
    # Add history (System prompt + previous chats)
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})
        
    # Add the newest user message if it's not already in history
    if messages[-1]['content'] != user_message:
         messages.append({"role": "user", "content": user_message})

    try:
        print(f"💬 Chatting... (Context Length: {len(str(messages))} chars)")
        
        # 3. Call the AI
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7, # Slightly creative for conversation
            max_tokens=500
        )
        
        reply = response.choices[0].message.content
        return reply

    except Exception as e:
        print(f"❌ Chat Error: {e}")
        return "I'm having trouble connecting to the brain right now. Please try again."