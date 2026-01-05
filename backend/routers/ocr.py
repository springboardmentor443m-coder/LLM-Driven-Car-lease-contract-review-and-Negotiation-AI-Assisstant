from fastapi import APIRouter, UploadFile, File, HTTPException
from services.ocr_service import extract_text_from_file

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Accepts PDF or Image, performs OCR, and returns raw text.
    """
    # Read file bytes
    contents = await file.read()
    
    # Send to OCR Service
    result = await extract_text_from_file(contents, file.filename)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result