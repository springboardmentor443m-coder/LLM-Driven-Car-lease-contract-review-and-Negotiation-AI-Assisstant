
# backend/routers/vin.py
from fastapi import APIRouter, HTTPException
from services import vin_service
from services.valuation_service import get_vehicle_valuation, calculate_score

router = APIRouter()

@router.get("/decode/{vin}")
async def decode_vehicle_vin(vin: str):
    if len(vin) != 17:
         raise HTTPException(status_code=400, detail="VIN must be exactly 17 characters")
    
    # We await the function because it uses httpx (async)
    result = await vin_service.get_vehicle_details(vin)
    
    if not result:
        raise HTTPException(status_code=404, detail="Vehicle not found or VIN invalid")
        
    return result

@router.get("/valuation/{vin}")
async def get_valuation(vin: str, contract_price: float = 0.0, money_factor: float = 0.0):
    """
    Fetches complete vehicle valuation including NHTSA data and market value.
    Returns vehicle details, market data, and fairness score.
    
    Query parameters:
    - contract_price: Optional contract price (monthly payment or total) for fairness calculation
    - money_factor: Optional money factor for fairness calculation
    """
    if len(vin) != 17:
        raise HTTPException(status_code=400, detail="VIN must be exactly 17 characters")
    
    try:
        # Get NHTSA details
        nhtsa_details = await vin_service.get_vehicle_details(vin)
        
        # Get vehicle valuation (NHTSA + Market Price)
        vehicle_details, market_price = await get_vehicle_valuation(vin)
        
        # Merge NHTSA details into vehicle_details if available
        if nhtsa_details:
            vehicle_details.update({
                "make": nhtsa_details.get("Make") or vehicle_details.get("make"),
                "model": nhtsa_details.get("Model") or vehicle_details.get("model"),
                "year": int(nhtsa_details.get("Model Year") or vehicle_details.get("year") or 2024),
                "trim": nhtsa_details.get("Trim") or vehicle_details.get("trim"),
                "body_class": nhtsa_details.get("Body Class"),
                "engine_hp": nhtsa_details.get("Engine HP"),
            })
        
        # Calculate fairness score if we have both contract price and market price
        if contract_price > 0 and market_price > 0:
            fairness_data = calculate_score(contract_price, market_price, money_factor)
        elif market_price > 0:
            # If we have market price but no contract price, show a neutral score
            fairness_data = {
                "score": 50,
                "rating": "Pending",
                "reasons": ["Market value verified. Add the contract price to generate a precise fairness score and red-flag review."]
            }
        else:
            # No market price available
            fairness_data = {
                "score": 0,
                "rating": "Unknown",
                "reasons": ["Market value is unavailable, so a fairness score cannot be calculated yet."]
            }
        
        return {
            "vin": vin,
            "vehicle_details": vehicle_details,
            "nhtsa_details": nhtsa_details or {},
            "market_data": {
                "market_average": market_price,
                "estimated_price": market_price,
                "contract_price": contract_price,
            },
            "fairness_score": fairness_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching valuation: {str(e)}")
