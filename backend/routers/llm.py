from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re
import traceback
from typing import Any, Dict
from services.llm_service import analyze_lease, chat_negotiation
from services.valuation_service import get_vehicle_valuation, calculate_score

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

# Updated section for backend/routers/llm.py
@router.post("/full-analysis")
async def full_analysis_endpoint(request: AnalysisRequest):
    result = await analyze_lease(request.text)
    
    # Extract market price from the analysis result
    market_data = result.get("rapidapi_details") or {}
    market_price = _parse_money(market_data.get("estimated_price") or 0)
    
    # Extract all SLA factors for comprehensive scoring
    sla = result.get("sla_extraction") or {}
    contract_monthly = _parse_money(sla.get("monthly_payment") or 0)
    money_factor_str = sla.get("interest_rate_apr") or "0"
    money_factor = _parse_money(money_factor_str) / 100.0 if "%" not in str(money_factor_str) else _parse_money(money_factor_str.replace("%", "")) / 100.0
    residual_value = _parse_money(sla.get("residual_value") or 0)
    mileage_allowance = _parse_money(sla.get("mileage_allowance_per_year") or 12000)
    excess_mileage_fee = _parse_money(sla.get("excess_mileage_fee") or 0)
    lease_term = _parse_money(sla.get("lease_term_months") or 36)
    
    # Calculate Fairness based on all factors
    fairness_result = calculate_score(
        contract_price=contract_monthly,
        market_price=market_price,
        money_factor=money_factor,
        residual_value=residual_value,
        mileage_allowance=mileage_allowance,
        excess_mileage_fee=excess_mileage_fee,
        lease_term_months=lease_term
    ) if market_price > 0 else {"score": 50, "rating": "Unknown", "reasons": []}

    return {
        **result,
        "market_data": {
            "market_average": market_price,
            "contract_price": contract_monthly,
            "buyout_price": residual_value,
            "ai_verdict": "Fair" if market_price == 0 or contract_monthly < (market_price * 0.015) else "Overpriced"
        },
        "fairness_score": fairness_result
    }
@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Fixed: Now registered under the /llm prefix."""
    try:
        response = await chat_negotiation(request.history, request.message)
        return {"response": response}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))