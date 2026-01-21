import os
from fastapi import APIRouter, HTTPException
from app.services.sla_extractor import extract_sla
from app.config import UPLOAD_DIR

router = APIRouter()

@router.get("/sla/{batch_id}/{filename}")
def extract_sla_from_contract(batch_id: str, filename: str):
    text_file = os.path.join(UPLOAD_DIR, batch_id, f"{filename}.txt")

    if not os.path.exists(text_file):
        raise HTTPException(status_code=404, detail="OCR text not found")

    with open(text_file, "r", encoding="utf-8") as f:
        ocr_text = f.read()

    try:
        sla_data = extract_sla(ocr_text)
        return {
            "batch_id": batch_id,
            "filename": filename,
            "sla": sla_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
