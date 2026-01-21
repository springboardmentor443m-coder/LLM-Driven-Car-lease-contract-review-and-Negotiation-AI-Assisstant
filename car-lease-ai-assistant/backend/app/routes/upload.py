# backend/app/routes/upload.py

import os
import uuid
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import UPLOAD_DIR, MAX_FILES

router = APIRouter()   # 🔴 THIS LINE IS MANDATORY


@router.post("/upload")
async def upload_contracts(files: List[UploadFile] = File(...)):
    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_FILES} files allowed"
        )

    batch_id = str(uuid.uuid4())
    batch_path = os.path.join(UPLOAD_DIR, batch_id)
    os.makedirs(batch_path, exist_ok=True)

    contracts = []

    for idx, file in enumerate(files):
        file_path = os.path.join(batch_path, f"contract_{idx+1}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(await file.read())

        contracts.append({
            "contract_id": f"{batch_id}_{idx+1}",
            "filename": f"contract_{idx+1}_{file.filename}"
        })

    return {
        "batch_id": batch_id,
        "contracts": contracts,
        "status": "uploaded"
    }
