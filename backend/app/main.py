import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models, ocr, llm_extract, nhtsa

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Car Lease/Loan Contract Review API")

# ✅ CORS FIX — allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow all origins (or put "http://localhost:3000")
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload")
async def upload_contract(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith((".pdf", ".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="Only pdf/images accepted")

    contents = await file.read()
    text = ocr.pdf_bytes_to_text(contents)

    c = models.Contract(filename=file.filename, text=text)
    db.add(c)
    db.commit()
    db.refresh(c)

    extracted = llm_extract.extract_sla_from_text(text)
    c.extracted = extracted
    db.add(c)
    db.commit()
    db.refresh(c)

    return JSONResponse({"id": c.id, "filename": c.filename, "extracted": c.extracted})

@app.get("/contract/{contract_id}")
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    c = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "id": c.id,
        "filename": c.filename,
        "text": c.text,
        "extracted": c.extracted,
        "created_at": c.created_at
    }

@app.get("/vin/{vin}")
def vin_lookup(vin: str):
    return nhtsa.lookup_vin(vin)

@app.get("/health")
def health():
    return {"status": "ok"}
