from fastapi import FastAPI

app = FastAPI(title="Car Lease AI Assistant")

@app.get("/")
def root():
    return {"status": "Backend running"}


from fastapi import FastAPI, UploadFile, File
import shutil
import os

from backend.ocr.ocr_engine import extract_text

app = FastAPI(title="Car Lease AI Assistant")

UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"status": "Backend running successfully"}


@app.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text(file_path)

    return {
        "message": "File uploaded and processed successfully",
        "text_preview": extracted_text[:500]
    }

from fastapi import FastAPI, UploadFile, File
import shutil
import os

from backend.ocr.ocr_engine import extract_text
from backend.llm.sla_extractor import extract_sla

app = FastAPI(title="Car Lease AI Assistant")

UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"status": "Backend running successfully"}


@app.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text(file_path)

    return {
        "message": "File uploaded and processed successfully",
        "text_preview": extracted_text[:500],
        "full_text": extracted_text
    }


@app.post("/extract-sla")
async def extract_sla_api(contract_text: str):
    sla_data = extract_sla(contract_text)
    return {
        "sla": sla_data
    }






