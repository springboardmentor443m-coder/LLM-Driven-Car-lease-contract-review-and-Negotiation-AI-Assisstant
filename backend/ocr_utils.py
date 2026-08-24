import os
import base64
import json
import io

from groq import Groq
from pdfminer.high_level import extract_text


# ======================================================
# GROQ CONFIG
# ======================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client only when API key exists
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# ======================================================
# MODELS
# ======================================================

# Used for text-based SLA extraction
# This model is available with your current Groq API key.
SLA_MODEL = "openai/gpt-oss-120b"


# Used for image OCR.
# IMPORTANT:
# Your current Groq API key does NOT have this model available.
# Therefore, JPG/PNG OCR through Groq is currently unavailable.
#
# We keep the variable here so image OCR can be replaced later
# with another vision/OCR solution.
OCR_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


# ======================================================
# OCR FUNCTION (PHASE 3)
# ======================================================

def extract_text_from_image(
    image_bytes: bytes,
    content_type: str = "image/jpeg"
) -> str:
    """
    Extract text from image bytes using a vision-capable LLM.

    FAIL-SAFE:
    Never crashes the FastAPI backend.
    """

    if not client:
        print("⚠️ GROQ_API_KEY not set – OCR skipped")
        return ""

    try:
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        completion = client.chat.completions.create(
            model=OCR_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Extract all readable text from this image. "
                                "Return only the extracted text."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": (
                                    f"data:{content_type};"
                                    f"base64,{image_base64}"
                                )
                            }
                        }
                    ]
                }
            ],
            temperature=0,
            max_completion_tokens=1024,
        )

        text = completion.choices[0].message.content

        if not text:
            print("⚠️ OCR returned empty text")
            return ""

        text = text.strip()

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

    FAIL-SAFE:
    Never crashes the backend.

    Returns:
        Dictionary containing:
        - apr
        - lease_term
        - monthly_payment
        - mileage_limit
        - early_termination
        - penalties
        - fairness_score
    """

    if not client:
        print("⚠️ GROQ_API_KEY not set – SLA extraction skipped")
        return default_sla()

    if not text or len(text.strip()) < 20:
        print("⚠️ Contract text is too short for SLA extraction")
        return default_sla()

    prompt = f"""
You are an AI assistant specialized in car loan and lease contract analysis.

Extract the following information from the contract text.

Return ONLY valid JSON.
Do NOT include markdown.
Do NOT include explanations.

Required JSON keys:

apr
lease_term
monthly_payment
mileage_limit
early_termination
penalties
fairness_score

Rules:

1. Use only information present in the contract.
2. Do not guess missing information.
3. If a value is missing, return "Unknown".
4. fairness_score must be an integer between 0 and 100.
5. Keep numerical values as numbers whenever possible.

Contract Text:
{text}
"""

    try:

        completion = client.chat.completions.create(
            model=SLA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_completion_tokens=512,
        )

        response = completion.choices[0].message.content

        if not response:
            print("⚠️ LLM returned empty SLA response")
            return default_sla()

        response = response.strip()

        # ==================================================
        # REMOVE MARKDOWN JSON WRAPPER
        # ==================================================

        if response.startswith("```"):

            response = response.replace("```json", "")
            response = response.replace("```JSON", "")
            response = response.replace("```", "")
            response = response.strip()

        # ==================================================
        # PARSE JSON
        # ==================================================

        parsed = json.loads(response)

        if not isinstance(parsed, dict):
            print("⚠️ LLM returned invalid JSON structure")
            return default_sla()

        # ==================================================
        # SAFE FAIRNESS SCORE
        # ==================================================

        fairness_raw = parsed.get("fairness_score", 5)

        try:
            fairness_score = int(float(fairness_raw))
        except (ValueError, TypeError):
            fairness_score = 5

        # Keep score between 0 and 100
        fairness_score = max(0, min(100, fairness_score))

        # ==================================================
        # RETURN CLEAN SLA DATA
        # ==================================================

        return {
            "apr": str(
                parsed.get("apr", "Unknown")
            ),

            "lease_term": str(
                parsed.get("lease_term", "Unknown")
            ),

            "monthly_payment": str(
                parsed.get("monthly_payment", "Unknown")
            ),

            "mileage_limit": str(
                parsed.get("mileage_limit", "Unknown")
            ),

            "early_termination": str(
                parsed.get("early_termination", "Unknown")
            ),

            "penalties": str(
                parsed.get("penalties", "Unknown")
            ),

            "fairness_score": fairness_score
        }

    except json.JSONDecodeError as e:

        print("⚠️ SLA JSON parsing failed:", str(e))
        print("LLM response:", response if "response" in locals() else "")

        return default_sla()

    except Exception as e:

        print("⚠️ SLA extraction failed:", str(e))

        return default_sla()


# ======================================================
# DEFAULT SLA
# ======================================================

def default_sla() -> dict:
    """
    Safe fallback when LLM extraction fails.
    """

    return {
        "apr": "Unknown",
        "lease_term": "Unknown",
        "monthly_payment": "Unknown",
        "mileage_limit": "Unknown",
        "early_termination": "Unknown",
        "penalties": "Unknown",
        "fairness_score": 5
    }


# ======================================================
# PDF TEXT EXTRACTION
# ======================================================

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF bytes using pdfminer.

    FAIL-SAFE:
    Never crashes the backend.
    """

    try:

        text = extract_text(
            io.BytesIO(pdf_bytes)
        )

        if not text:
            print("⚠️ PDF extraction returned empty text")
            return ""

        return text.strip()

    except Exception as e:

        print("⚠️ PDF extraction failed:", str(e))

        return ""