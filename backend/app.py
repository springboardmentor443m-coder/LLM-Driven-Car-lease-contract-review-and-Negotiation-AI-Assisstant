# ================================================================
# app.py — Car Contract AI Backend (Complete with Chatbot)
# ================================================================

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import re
import json
import requests
import tempfile
import traceback
import time
from typing import Optional, Dict
import io
import sys

# OCR
from pdf2image import convert_from_path
import pytesseract
from PyPDF2 import PdfReader

# Internal modules
from premium_report import build_comparison_pdf_bytes, build_negotiation_pdf
from extractor import extract_with_llm, extract_with_regex
from summarizer import call_summary_llm
from fairness_engine import calculate_fairness_score
from negotiator import generate_negotiation_messages

# LLM provider
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

# ================================================================
# FASTAPI SETUP
# ================================================================
app = FastAPI(title="Car Contract AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ================================================================
# GLOBAL CONFIG
# ================================================================
POPPLER_PATH = os.getenv("POPPLER_PATH")
TESSERACT_CMD = os.getenv("TESSERACT_CMD")

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

print("DEBUG POPPLER_PATH =", POPPLER_PATH)

# ================================================================
# UTILITIES
# ================================================================
def clean_text(s: str) -> str:
    s = re.sub(r"[\x0c\x0b\r]", "", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def extract_pdf_text_direct(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except:
        return ""


def extract_text_from_pdf(pdf_path, poppler_path=None, dpi=300):
    convert_kwargs = {"dpi": dpi}
    if poppler_path:
        convert_kwargs["poppler_path"] = poppler_path

    pages = convert_from_path(pdf_path, **convert_kwargs)
    out = []

    for i, img in enumerate(pages):
        try:
            txt = pytesseract.image_to_string(img)
            out.append(f"--- PAGE {i+1} ---\n{txt}")
        except Exception as e:
            print("[OCR ERROR] Page", i+1, e, file=sys.stderr)

    return "\n".join(out)


def filter_empty_fields(data):
    """Remove empty strings, None, empty lists, empty dicts recursively."""
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if v in ("", None, [], {}):
                continue
            val = filter_empty_fields(v)
            if val not in ("", None, [], {}):
                cleaned[k] = val
        return cleaned

    elif isinstance(data, list):
        cleaned_list = []
        for item in data:
            if item in ("", None, [], {}):
                continue
            val = filter_empty_fields(item)
            if val not in ("", None, [], {}):
                cleaned_list.append(val)
        return cleaned_list

    return data


IMPORTANT_FIELDS = {
    "buyer_name", "seller_name", "vin",
    "year", "make", "model", "trim",
    "monthly_payment", "down_payment",
    "security_deposit", "money_factor", "interest_rate",
    "residual_value", "buyout_price",
    "acquisition_fee", "documentation_fee",
    "processing_fee", "dealer_conveyance_fee",
    "disposition_fee", "excess_mileage_fee",
    "msrp", "vehicle_price",
    "capitalized_cost", "adjusted_cap_cost",
    "term_months", "annual_mileage", "apr"
}

def keep_only_important_fields(data: dict) -> dict:
    result = {}
    for key, value in data.items():
        if key in IMPORTANT_FIELDS and value not in ("", None, [], {}):
            result[key] = value
    return result

# ================================================================
# GLOBAL ERROR HANDLER
# ================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("[UNHANDLED ERROR]\n", traceback.format_exc(), file=sys.stderr)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


# ================================================================
# ROOT
# ================================================================
@app.get("/")
def home():
    return {"status": "Car Contract AI Backend Running"}


# ================================================================
# EXTRACTION ENDPOINT
# ================================================================
@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    tmp_path = None
    try:
        pdf_bytes = await file.read()
        if not pdf_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp.flush()
            tmp_path = tmp.name

        # Digital extraction
        raw_text = extract_pdf_text_direct(tmp_path)
        method = "digital"

        if not raw_text.strip():
            # OCR fallback
            raw_text = extract_text_from_pdf(tmp_path, POPPLER_PATH)
            method = "ocr"

        cleaned_text = clean_text(raw_text)

        # LLM extraction
        try:
            fields = extract_with_llm(cleaned_text)
            if "error" in fields:
                fields = extract_with_regex(cleaned_text)
                extraction_method = "regex_fallback"
            else:
                extraction_method = "llm"
        except:
            fields = extract_with_regex(cleaned_text)
            extraction_method = "regex_fallback"

        # Remove empty fields
        full_cleaned = filter_empty_fields(fields)

        # Extract important fields
        important_cleaned = keep_only_important_fields(full_cleaned.get("core", {}))

        return {
            "raw_text": raw_text,
            "extracted_text": cleaned_text,
            "llm_structured_data_full": full_cleaned,
            "llm_structured_data_important": important_cleaned,
            "llm_structured_data": full_cleaned,  # For backward compatibility
            "extraction_method": extraction_method,
            "ocr_method": method
        }

    except Exception as e:
        print("[EXTRACT ERROR]", traceback.format_exc(), file=sys.stderr)
        raise HTTPException(500, f"Extraction failed: {e}")

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try: os.remove(tmp_path)
            except: pass

# ================================================================
# VIN LOOKUP
# ================================================================
def validate_vin(vin: str):
    return (
        len(vin) == 17
        and not re.search(r"[IOQ]", vin)
        and bool(re.match(r"^[A-HJ-NPR-Z0-9]{17}$", vin))
    )

@app.get("/vin/{vin}")
async def vin_lookup(vin: str):
    vin = vin.upper().strip()
    if not validate_vin(vin):
        return {
            "status": "invalid",
            "message": "Invalid VIN format. Must be 17 characters, no I/O/Q."
        }

    nhtsa_url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"

    for attempt in range(3):
        try:
            response = requests.get(nhtsa_url, timeout=25)
            response.raise_for_status()
            data = response.json()
            break
        except Exception as e:
            if attempt == 2:
                return {
                    "status": "error",
                    "vin": vin,
                    "message": "NHTSA API unreachable or timed out."
                }
            time.sleep(2)

    results = data.get("Results", [])
    if not results:
        return {"status": "not_found", "vin": vin}

    def get_field(variable_id):
        for item in results:
            if item.get("VariableId") == variable_id and item.get("Value"):
                return item["Value"]
        return "N/A"

    summary = {
        "vin": vin,
        "year": get_field(29),
        "make": get_field(26),
        "model": get_field(28),
        "trim": get_field(109),
        "body_class": get_field(5),
        "engine": get_field(13),
        "fuel": get_field(24),
        "transmission": get_field(37),
        "drive_type": get_field(15),
        "manufactured_in": get_field(75),
        "manufacturer": get_field(27),
        "vehicle_type": get_field(39),
        "doors": get_field(14),
        "raw": results
    }

    if summary["year"] == "N/A":
        return {"status": "not_found", "summary": summary}

    return {"status": "found", "vin": vin, "summary": summary}


# ================================================================
# SUMMARY + FAIRNESS + NEGOTIATION
# ================================================================
@app.post("/summarize")
async def summarize_contract(payload: dict):
    try:
        raw = payload.get("raw_text", "")
        structured = payload.get("llm_structured_data_full", {})

        score, reasons = calculate_fairness_score(structured)
        summary = call_summary_llm(raw, structured)
        negotiation = generate_negotiation_messages(structured, score, reasons)

        return {
            "summary": summary,
            "fairness_score": score,
            "score_reasons": reasons,
            "negotiation_tips": negotiation
        }

    except Exception as e:
        print("[SUMMARIZE ERROR]", traceback.format_exc(), file=sys.stderr)
        raise HTTPException(500, f"Summary failed: {e}")


# ================================================================
# OFFER COMPARISON
# ================================================================
@app.post("/compare_offers")
def compare_offers(payload: dict):
    A = payload.get("offer_a", {})
    B = payload.get("offer_b", {})

    score_a, reasons_a = calculate_fairness_score(A)
    score_b, reasons_b = calculate_fairness_score(B)

    best = (
        "A" if score_a > score_b
        else "B" if score_b > score_a
        else "Tie"
    )

    return {
        "offer_a": {"fields": A, "score": score_a, "reasons": reasons_a},
        "offer_b": {"fields": B, "score": score_b, "reasons": reasons_b},
        "best_offer": best
    }


# ================================================================
# CHATBOT ENDPOINT
# ================================================================
@app.post("/chat")
async def chat(payload: dict):
    """Answer user questions about their contract using AI."""
    try:
        raw_text = payload.get("raw_text", "")
        extracted_fields = payload.get("extracted_fields", {})
        question = payload.get("question", "")
        
        if not question:
            return {"answer": "Please ask a question."}
        
        # Build context
        context_parts = []
        if extracted_fields and "core" in extracted_fields:
            core = extracted_fields["core"]
            context_parts.append("CONTRACT DETAILS:")
            for key, value in core.items():
                if value and value not in ("", "N/A", None):
                    context_parts.append(f"- {key}: {value}")
        
        if raw_text:
            context_parts.append(f"\nFULL CONTRACT TEXT:\n{raw_text[:6000]}")
        
        context = "\n".join(context_parts)
        
        prompt = f"""You are a helpful car contract advisor. Answer the user's question based ONLY on the contract information provided below. If the information is not in the contract, say so.

{context}

USER QUESTION: {question}

Provide a clear, helpful answer:"""

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=500,
            messages=[
                {"role": "system", "content": "You are a car contract advisor. Be helpful, concise, and accurate."},
                {"role": "user", "content": prompt}
            ]
        )
        
        answer = response.choices[0].message.content
        return {"answer": answer}
        
    except Exception as e:
        print(f"[CHAT ERROR] {traceback.format_exc()}", file=sys.stderr)
        return {"answer": f"I encountered an error: {str(e)}. Please try again."}


# ================================================================
# PDF EXPORT ENDPOINTS
# ================================================================
@app.post("/report")
def report(payload: dict):
    pdf = build_comparison_pdf_bytes(
        payload.get("meta", {}),
        payload.get("summary", {}),
        payload.get("compare", {})
    )
    return StreamingResponse(io.BytesIO(pdf), media_type="application/pdf")


@app.post("/negotiation_pdf")
def negotiation_pdf(payload: dict):
    pdf = build_negotiation_pdf(
        payload.get("summary", {}),
        payload.get("fairness_score", 0),
        payload.get("score_reasons", []),
        payload.get("negotiation_tips", {}),
        payload.get("structured_data", {})
    )
    return StreamingResponse(io.BytesIO(pdf), media_type="application/pdf")


# ================================================================
# RUN SERVER
# ================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)