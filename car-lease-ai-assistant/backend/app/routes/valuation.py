from fastapi import APIRouter, HTTPException
from datetime import datetime
import os
import json

from app.services.carsapi_service import get_msrp_from_carsapi
from app.services.vin_service import extract_vin, decode_vin

router = APIRouter()


# -------------------------------
# Residual Value Calculation
# -------------------------------
def calculate_residual_value(
    msrp: float,
    year: int,
    mileage: float = 75000,
    condition: str = "good"
) -> dict:
    current_year = datetime.now().year
    age_years = current_year - year

    annual_depreciation_rate = 0.15
    baseline_value = msrp * ((1 - annual_depreciation_rate) ** age_years)

    condition_factors = {
        "excellent": 0.97,
        "good": 0.92,
        "fair": 0.85,
        "poor": 0.75
    }
    condition_factor = condition_factors.get(condition, 0.92)

    expected_mileage = age_years * 12000
    mileage_factor = 1.0
    if mileage > expected_mileage:
        mileage_factor -= min((mileage - expected_mileage) / 100000, 0.15)

    final_value = baseline_value * condition_factor * mileage_factor

    return {
        "year": year,
        "age_years": age_years,
        "msrp": msrp,
        "baseline_value": round(baseline_value, 2),
        "condition": condition,
        "condition_factor": condition_factor,
        "mileage": mileage,
        "mileage_factor": round(mileage_factor, 2),
        "final_value": round(final_value, 2)
    }


# -------------------------------
# Fair Lease Calculation
# -------------------------------
def calculate_fair_lease(
    msrp: float,
    residual_value: float,
    lease_term_months: int = 36,
    apr: float = 8.5
) -> dict:
    money_factor = apr / 2400

    depreciation_fee = (msrp - residual_value) / lease_term_months
    finance_fee = (msrp + residual_value) * money_factor
    monthly_payment = depreciation_fee + finance_fee

    return {
        "lease_term_months": lease_term_months,
        "apr": apr,
        "money_factor": round(money_factor, 6),
        "depreciation_fee": round(depreciation_fee, 2),
        "finance_fee": round(finance_fee, 2),
        "fair_monthly_lease": round(monthly_payment, 2)
    }


# -------------------------------
# MAIN VALUATION ENDPOINT
# -------------------------------
@router.get("/{batch_id}/{filename}")
def valuation_pipeline(batch_id: str, filename: str):
    # ---- Load OCR text ----
    txt_path = f"uploads/{batch_id}/{filename}.txt"

    if not os.path.exists(txt_path):
        raise HTTPException(status_code=404, detail="OCR text not found")

    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read()

    # ---- VIN extraction ----
    vin = extract_vin(text)
    if not vin:
        raise HTTPException(status_code=404, detail="VIN not found")

    # ---- VIN decode (best-effort) ----
    vehicle = decode_vin(vin) or {}

    make = vehicle.get("make") or vehicle.get("Make")
    model = vehicle.get("model") or vehicle.get("Model")
    year = (
        vehicle.get("year")
        or vehicle.get("ModelYear")
        or vehicle.get("Model Year")
    )

    if not make or not model or not year:
        raise HTTPException(
            status_code=500,
            detail=f"VIN decode missing fields: {vehicle}"
        )

    year = int(year)

    # ---- Fetch MSRP ----
    msrp = get_msrp_from_carsapi(make, model, year)
    if not msrp:
        raise HTTPException(status_code=404, detail="MSRP not found")

    # ---- Residual value ----
    residual = calculate_residual_value(
        msrp=msrp,
        year=year,
        mileage=75000,
        condition="good"
    )

    # ---- Lease pricing ----
    lease = calculate_fair_lease(
        msrp=msrp,
        residual_value=residual["final_value"]
    )

    # ---- Final result ----
    result = {
        "vehicle": {
            "vin": vin,
            "make": make,
            "model": model,
            "year": year
        },
        "msrp": msrp,
        "residual_value": residual,
        "fair_lease_pricing": lease
    }

    # ---- SAVE VALUATION JSON ----
    valuation_dir = f"uploads/{batch_id}"
    os.makedirs(valuation_dir, exist_ok=True)

    valuation_file = os.path.join(
        valuation_dir,
        f"{filename}.valuation.json"
    )

    with open(valuation_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    return result
