# backend/utils.py
"""
Utility helpers for Loan/Lease Contract AI
"""

from typing import Dict
import re


# ============================================================
# INTERNAL VIN DECODER
# ============================================================

def decode_vin_nhtsa(vin: str) -> Dict:
    """
    Decode VIN using official NHTSA VPIC API.
    Returns raw decoded results.
    """
    import requests

    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ============================================================
# PUBLIC ENTRY POINT
# ============================================================

def decode_vin(vin: str) -> Dict:
    """
    Public VIN decode function
    """

    vin = (vin or "").strip().upper()

    # Basic VIN validation
    if len(vin) != 17:
        return {
            "status": "invalid",
            "message": "VIN must be exactly 17 characters"
        }

    if not re.match(r"^[A-HJ-NPR-Z0-9]{17}$", vin):
        return {
            "status": "invalid",
            "message": "VIN contains invalid characters"
        }

    try:
        data = decode_vin_nhtsa(vin)

        if not data or "Results" not in data:
            return {
                "status": "error",
                "message": "Invalid VIN response from NHTSA"
            }

        results = data["Results"]

        def get(field_name: str) -> str:
            for r in results:
                if r.get("Variable") == field_name and r.get("Value"):
                    return str(r.get("Value"))
            return "N/A"

        summary = {
            "vin": vin,
            "year": get("Model Year"),
            "make": get("Make"),
            "model": get("Model"),
            "trim": get("Trim"),
            "engine": get("Engine Configuration"),
            "fuel": get("Fuel Type - Primary"),
            "transmission": get("Transmission Style"),
            "body_class": get("Body Class"),
            "doors": get("Doors"),
            "drive_type": get("Drive Type"),
            "vehicle_type": get("Vehicle Type"),
            "manufacturer": get("Manufacturer Name"),
            "manufactured_in": get("Plant Country"),
            "raw": results
        }

        return {
            "status": "found",
            "summary": summary
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"VIN lookup failed: {str(e)}"
        }


# ============================================================
# OPTIONAL GENERIC HELPERS (SAFE TO EXTEND)
# ============================================================

def safe_float(value, default=None):
    """
    Safely convert value to float.
    """
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except Exception:
        return default


def safe_int(value, default=None):
    """
    Safely convert value to int.
    """
    try:
        return int(float(value))
    except Exception:
        return default
