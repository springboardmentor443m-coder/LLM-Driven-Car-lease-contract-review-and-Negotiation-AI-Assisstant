"""
Phase 5: Vehicle Intelligence Service

Responsibilities:
- Orchestrates vehicle data enrichment using VIN
- Uses CarAPI (commercial, limited tier)
- Uses NHTSA VIN Decoder (official US Govt, free)
- FAIL-SAFE: Never crashes backend
"""

from typing import Dict
from .carapi_client import get_vehicle_by_vin
from .nhtsa_client import decode_vin


def get_vehicle_intelligence(vin: str) -> Dict:
    """
    Main Phase 5 service function.
    Returns combined vehicle intelligence.
    """

    # Strict VIN validation (standard VIN = 17 chars)
    if not vin or len(vin) != 17:
        return {
            "vin": vin,
            "error": "Invalid VIN format"
        }

    # -------------------------
    # CarAPI (Primary source)
    # -------------------------
    try:
        carapi_data = get_vehicle_by_vin(vin)
    except Exception as e:
        carapi_data = {
            "error": "CarAPI failed",
            "details": str(e)
        }

    # -------------------------
    # NHTSA VIN Decoder (Fallback / Enrichment)
    # -------------------------
    try:
        nhtsa_data = decode_vin(vin)
    except Exception as e:
        nhtsa_data = {
            "error": "NHTSA decoding failed",
            "details": str(e)
        }

    return {
        "vin": vin,
        "vehicle_specs": carapi_data,
        "vehicle_insights": {
            "nhtsa_data": nhtsa_data,
            "data_sources": ["CarAPI", "NHTSA"]
        }
    }
