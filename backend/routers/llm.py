from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.llm_service import analyze_lease, chat_negotiation
# IMPORT THE NEW SERVICE HERE
from services.valuation_service import get_vehicle_valuation, calculate_score
import re

router = APIRouter()

class AnalysisRequest(BaseModel):
    text: str

class ChatRequest(BaseModel):
    history: list
    message: str

@router.post("/full-analysis")
async def full_analysis_endpoint(request: AnalysisRequest):
    """
    Analyzes the contract text using the Multi-Source Auditor Engine.
    AND fetches market data + calculates fairness score.
    """
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    # 1. Run the LLM Analysis first
    result = await analyze_lease(request.text)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    # 2. Extract Data for Valuation
    # We look for keys that your LLM extracts. Ensure your prompt asks for 'vin', 'gross_capitalized_cost', and 'money_factor'
    vin = result.get('vin')
    
    # Clean up price (remove '$' and ',')
    contract_price_raw = result.get('gross_capitalized_cost', '0')
    try:
        contract_price = float(re.sub(r'[^\d.]', '', str(contract_price_raw)))
    except:
        contract_price = 0.0

    money_factor = result.get('money_factor', 0)

    # 3. Fetch Market Data & Calculate Fairness
    valuation_details = {}
    market_price = 0
    fairness_data = {}

    if vin:
        # Fetch data from NHTSA / RapidAPI
        valuation_details, market_price = await get_vehicle_valuation(vin)
        
        # Calculate Score if we have prices
        if contract_price > 0 and market_price > 0:
            fairness_data = calculate_score(contract_price, market_price, money_factor)
        else:
            fairness_data = {
                "score": 0, 
                "rating": "Unknown", 
                "reasons": ["Could not extract valid Price or VIN to compare."]
            }
    else:
        # Handle missing VIN
        fairness_data = {
            "score": 0, 
            "rating": "Error", 
            "reasons": ["No VIN found in contract."]
        }

    # 4. Attach the new data to the response
    result['vehicle_details'] = valuation_details
    result['market_data'] = {
        "market_average": market_price,
        "contract_price": contract_price
    }
    result['fairness_score'] = fairness_data

    return result

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = await chat_negotiation(request.history, request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))