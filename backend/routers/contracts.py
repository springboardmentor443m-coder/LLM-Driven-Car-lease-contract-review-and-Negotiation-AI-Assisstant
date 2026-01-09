from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session
import re

from fastapi.responses import FileResponse

from ..db import get_db
from ..models import Contract, SLAExtraction
from ..schemas import ContractResponse
from ..ocr_utils import extract_text_from_image, extract_text_from_pdf
from ..services.sla_extractor import extract_sla_from_text
from ..services.vehicle_service import get_vehicle_intelligence
from ..services.fairness_engine import evaluate_contract_fairness
from ..services.report_generator import generate_contract_report

router = APIRouter(prefix="/contracts", tags=["contracts"])


# ======================================================
# PHASE 3: CONTRACT UPLOAD
# ======================================================
@router.post("/upload", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def upload_contract(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(400, "Only JPG, PNG, or PDF files are supported")

    file_bytes = await file.read()

    raw_text = (
        extract_text_from_pdf(file_bytes)
        if file.content_type == "application/pdf"
        else extract_text_from_image(file_bytes)
    )

    contract = Contract(
        file_name=file.filename,
        raw_text=raw_text or ""
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)

    return ContractResponse(
        id=contract.id,
        file_name=contract.file_name,
        raw_text=contract.raw_text,
        sla_extraction=None
    )


# ======================================================
# PHASE 4: SLA EXTRACTION
# ======================================================
@router.post("/{contract_id}/extract-sla")
def extract_sla_for_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter_by(id=contract_id).first()
    if not contract:
        raise HTTPException(404, "Contract not found")

    sla_data = extract_sla_from_text(contract.raw_text)

    sla = db.query(SLAExtraction).filter_by(contract_id=contract.id).first()
    if not sla:
        sla = SLAExtraction(contract_id=contract.id)
        db.add(sla)

    sla.apr = sla_data.get("apr")
    sla.lease_term = sla_data.get("lease_term")
    sla.monthly_payment = sla_data.get("monthly_payment")
    sla.mileage_limit = sla_data.get("mileage_limit")
    sla.early_termination = sla_data.get("early_termination")
    sla.penalties = sla_data.get("penalties")

    db.commit()
    db.refresh(sla)

    return {
        "contract_id": contract.id,
        "sla": sla_data
    }


# ======================================================
# PHASE 5: VEHICLE INTELLIGENCE
# ======================================================
@router.get("/{contract_id}/vehicle-info")
def get_vehicle_info(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter_by(id=contract_id).first()
    if not contract:
        raise HTTPException(404, "Contract not found")

    vin_match = re.search(r"\b[A-HJ-NPR-Z0-9]{17}\b", contract.raw_text)
    if not vin_match:
        return {"contract_id": contract.id, "error": "VIN not found"}

    vin = vin_match.group(0)

    try:
        vehicle_data = get_vehicle_intelligence(vin)
    except Exception:
        vehicle_data = {"error": "Vehicle API failed"}

    return {
        "contract_id": contract.id,
        "vin": vin,
        "vehicle_data": vehicle_data
    }


# ======================================================
# GET ALL CONTRACTS
# ======================================================
@router.get("/", response_model=list[ContractResponse])
def get_contracts(db: Session = Depends(get_db)):
    contracts = db.query(Contract).all()
    result = []

    for c in contracts:
        sla = c.sla_extraction

        result.append(
            ContractResponse(
                id=c.id,
                file_name=c.file_name,
                raw_text=c.raw_text,
                sla_extraction={
                    "apr": sla.apr,
                    "lease_term": sla.lease_term,
                    "monthly_payment": sla.monthly_payment,
                    "mileage_limit": sla.mileage_limit,
                    "early_termination": sla.early_termination,
                    "penalties": sla.penalties,
                } if sla else None
            )
        )

    return result


# ======================================================
# PHASE 6: PROS & CONS ANALYSIS (NEW ✅)
# ======================================================
@router.get("/{contract_id}/fairness")
def get_contract_analysis(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter_by(id=contract_id).first()
    if not contract or not contract.sla_extraction:
        raise HTTPException(404, "Contract or SLA not found")

    sla = contract.sla_extraction

    sla_dict = {
        "apr": sla.apr,
        "lease_term": sla.lease_term,
        "monthly_payment": sla.monthly_payment,
        "mileage_limit": sla.mileage_limit,
        "early_termination": sla.early_termination,
        "penalties": sla.penalties
    }

    analysis = evaluate_contract_fairness(sla_dict)

    return {
        "contract_id": contract.id,
        **analysis
    }


# ======================================================
# PHASE 7: CHATBOT
# ======================================================
@router.post("/{contract_id}/chat")
def chat_with_contract(contract_id: int, question: str, db: Session = Depends(get_db)):
    from ..services.chatbot_engine import generate_chat_response

    contract = db.query(Contract).filter_by(id=contract_id).first()
    if not contract or not contract.sla_extraction:
        raise HTTPException(404, "Contract or SLA not found")

    sla = contract.sla_extraction

    sla_dict = {
        "apr": sla.apr,
        "lease_term": sla.lease_term,
        "monthly_payment": sla.monthly_payment,
        "mileage_limit": sla.mileage_limit,
        "early_termination": sla.early_termination or "Unknown",
        "penalties": sla.penalties or "Unknown",
    }

    vin_match = re.search(r"\b[A-HJ-NPR-Z0-9]{17}\b", contract.raw_text)
    vehicle_info = get_vehicle_intelligence(vin_match.group(0)) if vin_match else None

    answer = generate_chat_response(
        question=question,
        contract_text=contract.raw_text,
        sla=sla_dict,
        vehicle_info=vehicle_info,
        chat_history=[]
    )

    return {
        "contract_id": contract_id,
        "question": question,
        "answer": answer
    }


# ======================================================
# PHASE 7A: REPORT (JSON)
# ======================================================
@router.get("/{contract_id}/report")
def get_contract_report(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter_by(id=contract_id).first()
    if not contract or not contract.sla_extraction:
        raise HTTPException(404, "Contract or SLA not found")

    sla = contract.sla_extraction

    sla_dict = {
        "apr": sla.apr,
        "lease_term": sla.lease_term,
        "monthly_payment": sla.monthly_payment,
        "mileage_limit": sla.mileage_limit,
        "early_termination": sla.early_termination,
        "penalties": sla.penalties
    }

    analysis = evaluate_contract_fairness(sla_dict)

    return {
        "contract_id": contract.id,
        "sla_summary": sla_dict,
        **analysis
    }


# ======================================================
# PHASE 7B: REPORT PDF
# ======================================================
@router.get("/{contract_id}/report/pdf")
def download_contract_report(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter_by(id=contract_id).first()
    if not contract or not contract.sla_extraction:
        raise HTTPException(404, "Contract or SLA not found")

    sla = contract.sla_extraction

    sla_dict = {
        "apr": sla.apr,
        "lease_term": sla.lease_term,
        "monthly_payment": sla.monthly_payment,
        "mileage_limit": sla.mileage_limit,
        "early_termination": sla.early_termination,
        "penalties": sla.penalties
    }

    analysis = evaluate_contract_fairness(sla_dict)

    vin_match = re.search(r"\b[A-HJ-NPR-Z0-9]{17}\b", contract.raw_text)
    vehicle_info = get_vehicle_intelligence(vin_match.group(0)) if vin_match else None

    pdf_path = generate_contract_report(
        contract_id=contract.id,
        sla=sla_dict,
        fairness=analysis,
        vehicle_info=vehicle_info
    )

    return FileResponse(
        pdf_path,
        filename=f"contract_report_{contract.id}.pdf",
        media_type="application/pdf"
    )
