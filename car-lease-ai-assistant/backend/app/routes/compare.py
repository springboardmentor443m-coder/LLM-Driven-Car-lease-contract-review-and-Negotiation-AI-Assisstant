from fastapi import APIRouter, HTTPException
import json
import os
from app.services.comparison_service import score_contracts

router = APIRouter()


@router.get("/{batch_id}")
def compare_contracts(batch_id: str):
    base_path = f"uploads/{batch_id}"
    files = [f for f in os.listdir(base_path) if f.endswith(".valuation.json")]

    if len(files) < 2:
        raise HTTPException(400, "Need at least 2 contracts to compare")

    contracts = []
    for f in files:
        with open(os.path.join(base_path, f), "r") as jf:
            contracts.append(json.load(jf))

    ranked = score_contracts(contracts)

    return {
        "best_deal": ranked[0],
        "comparison": ranked
    }
