# backend/routers/vin.py
from fastapi import APIRouter, HTTPException
from services import vin_service

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