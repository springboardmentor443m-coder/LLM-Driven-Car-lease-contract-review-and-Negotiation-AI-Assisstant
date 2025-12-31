from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from backend.ocr import extract_text_from_pdf
from backend.logic import extract_fields, calculate_fairness_score, negotiation_advice
from backend.VIN_NUM import verify_vin
from backend.price import get_market_price_by_vin
from backend.groqmodel import generate_summary
from backend.chatbot import chatbot_response

app = FastAPI(title="Car Lease AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        text = extract_text_from_pdf(await file.read())
        fields = extract_fields(text)

        vin_info = verify_vin(fields["vin"]) if "vin" in fields else {}
        market_price = (
            get_market_price_by_vin(vin_info)
            if vin_info.get("valid")
            else None
        )

        fairness_score, fairness_reasons = calculate_fairness_score(
            fields, market_price
        )
        tips = negotiation_advice(fields)
        summary = generate_summary(text)

        return {
            "summary": summary,
            "fields": fields,
            "vin_info": vin_info,
            "market_price": market_price,
            "fairness_score": fairness_score,
            "fairness_reasons": fairness_reasons,
            "negotiation_tips": tips
        }

    except Exception as e:
        return {
            "summary": "Summary could not be generated due to an error.",
            "error": str(e),
            "fields": {},
            "vin_info": {},
            "market_price": None,
            "fairness_score": 0,
            "fairness_reasons": [],
            "negotiation_tips": []
        }

@app.post("/chat")
async def chat(payload: dict):
    return {
        "answer": chatbot_response(payload["question"], payload["data"])
    }
