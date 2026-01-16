from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re
import traceback
from typing import Any, Dict
from services.llm_service import analyze_lease, chat_negotiation
from services.valuation_service import calculate_score
# Import your verified market service
from services.market_service import estimate_market_price 

router = APIRouter()

class AnalysisRequest(BaseModel):
    text: str

class ChatRequest(BaseModel):
    history: list
    message: str

def _parse_money(value: Any) -> float:
    if value is None: return 0.0
    try:
        cleaned = re.sub(r"[^0-9.]", "", str(value))
        return float(cleaned) if cleaned else 0.0
    except: return 0.0

@router.post("/full-analysis")
async def full_analysis_endpoint(request: AnalysisRequest):
    try:
        # 1. AI Analysis (Extracts SLA terms like monthly payment)
        result = await analyze_lease(request.text)
        
        # 2. Hard Regex Extraction for Market Valuation
        # This ensures we get the VIN/Miles even if the AI misses them
        vin_match = re.search(r'\b[A-HJ-NPR-Z0-9]{17}\b', request.text)
        mile_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*miles', request.text, re.IGNORECASE)
        
        extracted_vin = vin_match.group(0) if vin_match else None
        extracted_miles = int(mile_match.group(1).replace(",", "")) if mile_match else 15000

        # 3. Fetch Real-Time Market Price
        # We use your verified API logic here
        market_price = 0.0
        if extracted_vin:
            market_price = estimate_market_price(vin=extracted_vin, mileage=extracted_miles)

        # 4. Extract SLA factors for scoring
        sla = result.get("sla_extraction") or {}
        contract_monthly = _parse_money(sla.get("monthly_payment") or 0)
        
        # Interest/Money Factor parsing
        mf_raw = sla.get("interest_rate_apr") or "0"
        money_factor = _parse_money(mf_raw) / 100.0
        
        residual_value = _parse_money(sla.get("residual_value") or 0)
        mileage_allowance = extracted_miles # Use the regex extracted value
        excess_fee = _parse_money(sla.get("excess_mileage_fee") or 0.25)
        lease_term = _parse_money(sla.get("lease_term_months") or 36)
        
        # 5. Calculate Score using the real Market Price
        fairness_result = calculate_score(
            contract_monthly=contract_monthly,
            market_price=market_price,
            money_factor=money_factor,
            residual_value=residual_value,
            mileage_allowance=mileage_allowance,
            lease_term=lease_term
        )

        return {
            **result,
            "vin": extracted_vin,
            "mileage": extracted_miles,
            "market_data": {
                "market_average": market_price,
                "contract_price": contract_monthly,
                "buyout_price": residual_value,
                "equity": market_price - residual_value if market_price > 0 else 0,
                "ai_verdict": "Strategic" if (market_price - residual_value) > 2000 else "Standard"
            },
            "fairness_score": fairness_result
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = await chat_negotiation(request.history, request.message)
        return {"response": response}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))