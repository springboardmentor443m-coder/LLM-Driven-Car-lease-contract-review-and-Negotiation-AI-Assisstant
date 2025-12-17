# contract_extractor.py
# STEP-1: Extraction + Negotiation Suggestions (Corrected & Stable)

import re, json
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image
import pytesseract
from pytesseract import Output
from llm_groq import generate_llm_explanation_groq


# ------------------ BASIC HELPERS ------------------

def safe_float(value):
    try:
        return float(str(value).replace("%", "").replace(",", "").strip())
    except:
        return None

# ------------------ INPUT FILES ------------------

image_paths = sorted(Path('.').glob("page_*.png"))

# ------------------ OCR HELPERS ------------------

def ocr_images_to_texts(images: List[Path]) -> List[str]:
    texts = []
    for img_p in images:
        img = Image.open(img_p)
        texts.append(pytesseract.image_to_string(img, lang='eng'))
    return texts

def ocr_images_to_data(images: List[Path]):
    datas = []
    for img_p in images:
        img = Image.open(img_p)
        datas.append(pytesseract.image_to_data(img, output_type=Output.DICT, lang='eng'))
    return datas

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

# ------------------ EXTRACTION FUNCTION ------------------

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
    if apr is not None and apr >= 7.0:
        suggestions.append("APR is high. Try negotiating for a lower interest rate.")

    early_fee = safe_float(f.get("early_termination_fee"))
    if early_fee is not None and early_fee >= 600:
        suggestions.append("Early termination fee is high. Ask to reduce or remove it.")

    mileage = safe_float(f.get("mileage_allowance_per_year"))
    if mileage is not None and mileage < 12000:
        suggestions.append("Mileage allowance is low. Negotiate a higher mileage limit.")

    down_payment = safe_float(f.get("down_payment"))
    if down_payment is not None and down_payment >= 3000:
        suggestions.append("Down payment is high. Ask if it can be reduced.")

    monthly = safe_float(f.get("monthly_payment"))
    if monthly is not None and monthly >= 500:
        suggestions.append("Monthly payment is high. Try negotiating better terms.")

    result["negotiation_suggestions"] = suggestions


# ------------------ LLM-STYLE EXPLANATION MODULE ------------------

def generate_llm_explanation(result: Dict[str, Any]) -> None:
    """
    Generates a natural-language explanation of the contract
    based on extracted fields, risks, and negotiation suggestions.
    """

    fields = result.get("fields", {})
    suggestions = result.get("negotiation_suggestions", [])

    # -------- Summary --------
    summary_parts = []

    if fields.get("monthly_payment"):
        summary_parts.append(
            f"The monthly payment for this lease is {fields['monthly_payment']}."
        )

    if fields.get("interest_rate"):
        summary_parts.append(
            f"The interest rate (APR) mentioned in the contract is {fields['interest_rate']}%."
        )

    if fields.get("mileage_allowance_per_year"):
        summary_parts.append(
            f"The allowed annual mileage is {fields['mileage_allowance_per_year']} miles."
        )

    summary_text = " ".join(summary_parts) if summary_parts else \
        "This lease contract contains standard vehicle leasing terms."

    # -------- Risk Explanation --------
    risk_text = ""
    apr = safe_float(fields.get("interest_rate"))
    mileage = safe_float(fields.get("mileage_allowance_per_year"))

    if apr and apr >= 7.0:
        risk_text += "The interest rate is relatively high, which may increase the total lease cost. "

    if mileage and mileage < 12000:
        risk_text += "The mileage allowance is low, which could lead to extra charges if exceeded. "

    if not risk_text:
        risk_text = "No major financial risks were detected in this contract."

    # -------- Negotiation Explanation --------
    if suggestions:
        negotiation_text = "Based on the contract analysis, the following negotiation points are recommended: "
        negotiation_text += " ".join(suggestions)
    else:
        negotiation_text = "The contract terms appear reasonable, and no major negotiation points were identified."

    # -------- Attach to result --------
    result["llm_explanation"] = {
        "summary": summary_text,
        "risk_explanation": risk_text.strip(),
        "negotiation_advice": negotiation_text.strip()
    }

# ------------------ MAIN PIPELINE ------------------

def run_extraction():
    if not image_paths:
        raise RuntimeError("No page_*.png files found.")

    texts = ocr_images_to_texts(image_paths)
    result = extract_fields(texts)
    add_negotiation_suggestions(result)
    generate_llm_explanation(result)
    result["llm_groq_explanation"] = generate_llm_explanation_groq(result)



    Path("extracted_contract.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )

    print("✅ extracted_contract.json created")
    return result

# ------------------ RUN ------------------

if __name__ == "__main__":
    output = run_extraction()
    print(json.dumps(output, indent=2))
