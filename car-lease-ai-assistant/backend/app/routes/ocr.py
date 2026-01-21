import os
from fastapi import APIRouter, HTTPException
from app.config import UPLOAD_DIR
from app.services.pdf_text_extractor import extract_text_from_pdf

router = APIRouter()

@router.get("/ocr/{batch_id}/{filename}")
def run_ocr(batch_id: str, filename: str):
    file_path = os.path.join(UPLOAD_DIR, batch_id, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files supported for OCR in this version"
        )

    try:
        # 🔹 Extract text from PDF
        extracted_text = extract_text_from_pdf(file_path)

        if not extracted_text.strip():
            raise HTTPException(
                status_code=422,
                detail="No readable text found in PDF"
            )

        # 🔹 SAVE OCR TEXT (INSIDE FUNCTION — IMPORTANT)
        txt_path = os.path.join(
            UPLOAD_DIR,
            batch_id,
            f"{filename}.txt"
        )

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)

        return {
            "batch_id": batch_id,
            "filename": filename,
            "extracted_text_preview": extracted_text[:2000]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
