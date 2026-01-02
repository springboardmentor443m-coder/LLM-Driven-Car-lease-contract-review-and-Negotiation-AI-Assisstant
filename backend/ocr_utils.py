import os
import base64
import json
import io
from groq import Groq
from pdfminer.high_level import extract_text

# Load API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client only if key exists
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# ======================================================
# OCR FUNCTION (PHASE 3)
# ======================================================
def extract_text_from_image(image_bytes: bytes, content_type: str = "image/jpeg") -> str:
    """
    Extract text from image bytes using Groq.
    FAIL-SAFE: Never crashes backend.
    """
    if not client:
        print("⚠️ GROQ_API_KEY not set – OCR skipped")
        return ""

    try:
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all readable text from this image."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{content_type};base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            temperature=0,
            max_completion_tokens=1024,
        )

        text = completion.choices[0].message.content.strip()

        # Guard against bad OCR output
        if len(text) < 20:
            print("⚠️ OCR returned insufficient text")
            return ""

        return text

    except Exception as e:
        print("⚠️ OCR failed:", str(e))
        return ""


# ======================================================
# SLA EXTRACTION FUNCTION (PHASE 4)
# ======================================================
def extract_sla_info(text: str) -> dict:
    """
    Extract SLA information from contract text using AI.
    FAIL-SAFE: Never crashes backend.
    """
    if not client or not text or len(text.strip()) < 20:
        return default_sla()

    prompt = f"""
You are a legal contract analysis AI.

Extract the following information from the contract text.
Return ONLY valid JSON. Do NOT add explanations.
If a value is missing, use "Unknown".

Required JSON keys:
apr, lease_term, monthly_payment, mileage_limit,
early_termination, penalties, fairness_score

Contract Text:
{text}
"""

    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_completion_tokens=512,
        )

        response = completion.choices[0].message.content.strip()

        parsed = json.loads(response)

        # Safe parsing
        fairness_raw = parsed.get("fairness_score", 5)
        fairness_score = (
            int(fairness_raw)
            if str(fairness_raw).isdigit()
            else 5
        )

        return {
            "apr": str(parsed.get("apr", "Unknown")),
            "lease_term": str(parsed.get("lease_term", "Unknown")),
            "monthly_payment": str(parsed.get("monthly_payment", "Unknown")),
            "mileage_limit": str(parsed.get("mileage_limit", "Unknown")),
            "early_termination": str(parsed.get("early_termination", "Unknown")),
            "penalties": str(parsed.get("penalties", "Unknown")),
            "fairness_score": fairness_score
        }

    except Exception as e:
        print("⚠️ SLA extraction failed:", str(e))
        return default_sla()


# ======================================================
# DEFAULT SLA (SAFE FALLBACK)
# ======================================================
def default_sla():
    return {
        "apr": "Unknown",
        "lease_term": "Unknown",
        "monthly_payment": "Unknown",
        "mileage_limit": "Unknown",
        "early_termination": "Unknown",
        "penalties": "Unknown",
        "fairness_score": 5
    }


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF bytes.
    FAIL-SAFE: Never crashes backend.
    """
    try:
        text = extract_text(io.BytesIO(pdf_bytes))
        return text.strip() if text else ""
    except Exception as e:
        print("⚠️ PDF extraction failed:", e)
        return ""
