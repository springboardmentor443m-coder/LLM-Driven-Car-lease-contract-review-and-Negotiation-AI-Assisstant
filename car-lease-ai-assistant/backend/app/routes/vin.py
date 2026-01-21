import os
from fastapi import APIRouter, HTTPException
from app.config import UPLOAD_DIR
from app.services.vin_service import extract_vin, decode_vin, get_recalls

router = APIRouter()

@router.get("/vin/{batch_id}/{filename}")
def vin_lookup(batch_id: str, filename: str):
    txt_path = os.path.join(
        UPLOAD_DIR,
        batch_id,
        f"{filename}.txt"
    )

    if not os.path.exists(txt_path):
        raise HTTPException(status_code=404, detail="OCR text not found")

    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read()

    vin = extract_vin(text)
    if not vin:
        raise HTTPException(status_code=404, detail="VIN not found in contract")

    vehicle_info = decode_vin(vin)
    recalls = get_recalls(vin)

    return {
        "vin": vin,
        "vehicle_info": vehicle_info,
        "recall_count": len(recalls),
        "recalls": recalls,
        "note": "Recall data may be empty if NHTSA service is unavailable"
    }
