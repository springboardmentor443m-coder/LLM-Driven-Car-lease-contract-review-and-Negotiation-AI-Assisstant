from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.negotiation_ai import generate_negotiation_advice
import os

router = APIRouter()

class NegotiationRequest(BaseModel):
    batch_id: str
    filename: str
    question: str

@router.post("/negotiate")
def negotiate(req: NegotiationRequest):
    """
    Uses OCR text + user question to generate negotiation advice
    """

    # ---- Load OCR text ----
    ocr_path = f"uploads/{req.batch_id}/{req.filename}.txt"

    if not os.path.exists(ocr_path):
        raise HTTPException(
            status_code=404,
            detail="OCR text not found. Please run OCR first."
        )

    with open(ocr_path, "r", encoding="utf-8") as f:
        ocr_text = f.read()

    # ---- Call AI (ONLY text + question) ----
    answer = generate_negotiation_advice(
        ocr_text=ocr_text,
        question=req.question
    )

    return {"answer": answer}
