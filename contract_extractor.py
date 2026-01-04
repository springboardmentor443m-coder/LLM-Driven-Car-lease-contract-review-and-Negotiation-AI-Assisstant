
# contract_extractor.py
# STEP-1: OCR + Extraction + Negotiation (STABLE BASE VERSION)

import re, json
from pathlib import Path
from typing import List, Dict, Any
from PIL import Image
import pytesseract
from pytesseract import Output


# ------------------ BASIC HELPERS ------------------

def safe_float(value):
    try:
        return float(str(value).replace("%", "").replace(",", "").strip())
    except:
        return None


# ------------------ INPUT FILES ------------------

image_paths = sorted(Path(".").glob("page_*.png"))


# ------------------ OCR HELPERS ------------------

def ocr_images_to_texts(images: List[Path]) -> List[str]:
    texts = []
    for img_p in images:
        img = Image.open(img_p)
        texts.append(pytesseract.image_to_string(img, lang="eng"))
    return texts


# ------------------ REGEX PATTERNS ------------------

patterns = {
    "interest_rate": r'(?i)(?:APR|Annual Percentage Rate)[^\d]*([0-9]{1,2}(?:\.[0-9]+)?)',
    "monthly_payment": r'(?i)(?:Monthly Payment)[^\d]*\$?([0-9,]+)',
    "down_payment": r'(?i)(?:Down Payment)[^\d]*\$?([0-9,]+)',
    "residual_value": r'(?i)(?:Residual Value)[^\d]*\$?([0-9,]+)',
    "mileage_allowance_per_year": r'(?i)(?:Mileage Allowance|Miles per Year)[^\d]*([0-9,]+)',
    "early_termination_fee": r'(?i)(?:Early Termination Fee)[^\d]*\$?([0-9,]+)',
    "vin": r'\b([A-HJ-NPR-Z0-9]{17})\b',
    "email": r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})',
    "phone": r'(\+?\d{1,3}[-\s]?)?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}'
}


# ------------------ FIELD EXTRACTION ------------------

def extract_fields(texts: List[str]) -> Dict[str, Any]:
    combined = "\n".join(texts)
    fields = {}
    confidence = {}

    for field, pat in patterns.items():
        m = re.search(pat, combined)
        if m:
            value = m.group(1).replace(",", "").strip()
            fields[field] = value
            confidence[field] = round(min(1.0, max(0.5, len(value) / 10)), 2)

    return {
        "fields": fields,
        "confidence": confidence,
        "raw_text": combined
    }


# ------------------ NEGOTIATION SUGGESTIONS ------------------

def add_negotiation_suggestions(result: Dict[str, Any]) -> None:
    f = result["fields"]
    suggestions = []

    apr = safe_float(f.get("interest_rate"))
    if apr and apr >= 7:
        suggestions.append("APR is high. Try negotiating for a lower interest rate.")

    mileage = safe_float(f.get("mileage_allowance_per_year"))
    if mileage and mileage < 12000:
        suggestions.append("Mileage allowance is low. Negotiate a higher limit.")

    down = safe_float(f.get("down_payment"))
    if down and down >= 3000:
        suggestions.append("Down payment is high. Ask if it can be reduced.")

    monthly = safe_float(f.get("monthly_payment"))
    if monthly and monthly >= 500:
        suggestions.append("Monthly payment is high. Negotiate better terms.")

    result["negotiation_suggestions"] = suggestions


# ------------------ RULE-BASED EXPLANATION ------------------

def generate_simple_explanation(result: Dict[str, Any]) -> None:
    fields = result["fields"]
    suggestions = result.get("negotiation_suggestions", [])

    summary = []
    if "monthly_payment" in fields:
        summary.append(f"The monthly payment is {fields['monthly_payment']}.")
    if "interest_rate" in fields:
        summary.append(f"The APR is {fields['interest_rate']}%.")

    result["explanation"] = {
        "summary": " ".join(summary) if summary else "Standard lease contract detected.",
        "negotiation_advice": suggestions
    }


# ------------------ MAIN PIPELINE ------------------

def run_extraction():
    if not image_paths:
        raise RuntimeError("No page_*.png files found.")

    texts = ocr_images_to_texts(image_paths)
    result = extract_fields(texts)
    add_negotiation_suggestions(result)
    generate_simple_explanation(result)

    Path("extracted_contract.json").write_text(
        json.dumps(result, indent=2),
        encoding="utf-8"
    )

    print("✅ extracted_contract.json created")
    return result


# ------------------ RUN ------------------

if __name__ == "__main__":
    output = run_extraction()
    print(json.dumps(output, indent=2))
