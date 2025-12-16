# backend/extractor.py - FIXED VERSION
"""
ULTRA PRO extractor (Groq 8B primary + regex fallback).
FIXED: Ensures no RegexFlag or non-serializable objects are returned.
"""

import os
import re
import json
import traceback
from typing import Dict, Any

try:
    from groq import Groq
except Exception:
    Groq = None

GROQ_API_KEY = os.getenv("GROQ_API_KEY", None)
groq_client = None
if Groq is not None and GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
    except Exception:
        groq_client = None


def _safe_parse_json_from_text(text: str) -> Any:
    """Try to parse JSON from text."""
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return None
        return None


def extract_with_llm(text: str) -> Dict[str, Any]:
    """Use Groq 8B to extract contract fields."""
    
    if not isinstance(text, str):
        return {"error": "Input must be a string."}

    if not groq_client:
        return {"error": "Groq client not configured (GROQ_API_KEY missing)."}

    prompt = f"""
You are a precision extraction engine for car finance/lease/sales contracts.
Extract the requested structured information from the TEXT block below.
Return ONLY valid JSON. DO NOT include any explanatory text.

TEXT:
\"\"\"\n{text[:8000]}\n\"\"\"

IMPORTANT EXTRACTION RULES:
1. For buyer_name and seller_name: Extract FULL NAMES ONLY (e.g., "John Smith", "Acme Auto Finance")
   - DO NOT return just "Name" or placeholder text
   - Must be actual person/company names from the contract
   - If you can't find a real name, leave the field empty ""
2. For VIN: Must be exactly 17 characters
3. For monetary values: Include $ symbol and format as "$123.45"
4. For percentages: Include % symbol (e.g., "7.5%")
5. Extract actual contract data, not generic placeholders

Return JSON with EXACT structure:

{{
  "core": {{
    "buyer_name": "",
    "seller_name": "",
    "vin": "",
    "vehicle": "",
    "year": "",
    "make": "",
    "model": "",
    "contract_type": "",
    "term_months": "",
    "start_date": "",
    "end_date": "",
    "monthly_payment": "",
    "down_payment": "",
    "security_deposit": "",
    "documentation_fee": "",
    "acquisition_fee": "",
    "other_fees": [],
    "apr": "",
    "interest_rate": "",
    "residual_value": "",
    "buyout_price": "",
    "odometer_at_sale": ""
  }},
  "financial_analysis": {{
    "vehicle_price": "",
    "total_paid": "",
    "total_interest": "",
    "effective_apr": "",
    "payment_count": "",
    "payment_schedule": []
  }},
  "signature_audit": {{
    "buyer_signed": false,
    "seller_signed": false,
    "signature_blocks": []
  }},
  "risk_analysis": {{
    "risk_score": "",
    "high_risks": [],
    "medium_risks": [],
    "low_risks": []
  }},
  "raw_debug": {{
    "llm_raw": ""
  }}
}}

Important:
- If a field is missing, return empty string (not null).
- Extract REAL data from the contract, not placeholders or labels.
"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.0,
            messages=[
                {"role": "system", "content": "You are an expert contract extraction engine. Return only JSON."},
                {"role": "user", "content": prompt}
            ]
        )

        result_text = response.choices[0].message.content
        parsed = _safe_parse_json_from_text(result_text)
        
        if parsed is None:
            return {"error": "LLM returned non-JSON output", "raw": result_text}

        out = {
            "core": parsed.get("core", {}),
            "financial_analysis": parsed.get("financial_analysis", {}),
            "signature_audit": parsed.get("signature_audit", {}),
            "risk_analysis": parsed.get("risk_analysis", {}),
            "raw_debug": {"llm_raw": parsed.get("raw_debug", {}).get("llm_raw", result_text)}
        }
        return out

    except Exception as e:
        return {"error": f"Groq extraction failed: {str(e)}", "trace": traceback.format_exc()}


def extract_with_regex(text: str) -> Dict[str, Any]:
    """
    Lightweight heuristic extractor - FIXED to never return RegexFlag objects.
    All regex match objects are converted to strings immediately.
    """
    
    if not isinstance(text, str):
        text = str(text or "")

    # Normalize text
    txt = re.sub(r"\s+", " ", text)

    data_core = {
        "buyer_name": "",
        "seller_name": "",
        "vin": "",
        "vehicle": "",
        "year": "",
        "make": "",
        "model": "",
        "contract_type": "",
        "term_months": "",
        "start_date": "",
        "end_date": "",
        "monthly_payment": "",
        "down_payment": "",
        "security_deposit": "",
        "documentation_fee": "",
        "acquisition_fee": "",
        "other_fees": [],
        "apr": "",
        "interest_rate": "",
        "residual_value": "",
        "buyout_price": "",
        "odometer_at_sale": ""
    }

    fin = {
        "vehicle_price": "",
        "total_paid": "",
        "total_interest": "",
        "effective_apr": "",
        "payment_count": "",
        "payment_schedule": []
    }

    sig = {
        "buyer_signed": False,
        "seller_signed": False,
        "signature_blocks": []
    }

    risk = {
        "risk_score": "",
        "high_risks": [],
        "medium_risks": [],
        "low_risks": []
    }

    # VIN - FIXED: Immediately convert match to string
    vin_m = re.search(r"\b([A-HJ-NPR-Z0-9]{17})\b", text)
    if vin_m:
        data_core["vin"] = str(vin_m.group(1))

    # Price patterns - IMPROVED to match your format
    # Match: "High Bid: $14,469" or "Loan Amount: $14,469"
    price_patterns = [
        r"(?:High Bid|Loan Amount|Vehicle Price|Price)[:\s]*\$[\s]*([0-9]{1,3}(?:[,][0-9]{3})*(?:\.[0-9]{1,2})?)",
        r"\$[\s]*([0-9]{1,3}(?:[,][0-9]{3})*(?:\.[0-9]{1,2})?)"
    ]
    
    for pattern in price_patterns:
        price_m = re.search(pattern, text, re.IGNORECASE)
        if price_m:
            price_str = price_m.group(1).replace(",", "")
            fin["vehicle_price"] = f"${price_str}"
            break
    
    if not fin["vehicle_price"]:
        # Fallback: bare numbers
        bare_price = re.search(r"\b([0-9]{4,7})\b", text)
        if bare_price:
            fin["vehicle_price"] = f"${bare_price.group(1)}"

    # APR - IMPROVED to match "7.2% per annum" format
    apr_patterns = [
        r"Interest Rate[:\s]*([0-9]{1,2}(?:\.[0-9]{1,2})?)\s?%",
        r"APR[:\s]*([0-9]{1,2}(?:\.[0-9]{1,2})?)\s?%",
        r"\b([0-9]{1,2}(?:\.[0-9]{1,2})?)\s?%\s*(?:per annum|APR)",
    ]
    
    for pattern in apr_patterns:
        apr_m = re.search(pattern, text, re.IGNORECASE)
        if apr_m:
            data_core["apr"] = str(apr_m.group(1)) + "%"
            fin["effective_apr"] = data_core["apr"]
            data_core["interest_rate"] = data_core["apr"]
            break

    # Monthly payment - IMPROVED
    monthly_patterns = [
        r"Monthly payments?\s*(?:of)?\s*\$?\s*([0-9,]{2,6}(?:\.[0-9]{1,2})?)",
        r"EMI[:\s]*\$?\s*([0-9,]{2,6}(?:\.[0-9]{1,2})?)",
        r"\$\s*([0-9,]{2,6}(?:\.[0-9]{1,2})?)\s*(?:per month|monthly)",
    ]
    
    for pattern in monthly_patterns:
        monthly_m = re.search(pattern, text, re.IGNORECASE)
        if monthly_m:
            amount = monthly_m.group(1).replace(",", "")
            data_core["monthly_payment"] = f"${amount}"
            break

    # Term - IMPROVED to capture "60 months"
    term_patterns = [
        r"(?:for|of)\s*([0-9]{1,3})\s*(months?|years?)",
        r"(?:term|period)[:\s]*([0-9]{1,3})\s*(months?|years?)",
        r"([0-9]{1,3})\s*(months?|years?)\s*(?:term|period)",
    ]
    
    for pattern in term_patterns:
        term_m = re.search(pattern, text, re.IGNORECASE)
        if term_m:
            number = str(term_m.group(1))
            unit = str(term_m.group(2)).lower()
            months = number
            if "year" in unit:
                try:
                    months = str(int(number) * 12)
                except Exception:
                    months = number
            data_core["term_months"] = months
            break

    # Year - FIXED
    year_m = re.search(r"\b(19|20)\d{2}\b", text)
    if year_m:
        data_core["year"] = str(year_m.group(0))

    # Down payment - IMPROVED
    down_patterns = [
        r"Down Payment[:\s]*\$?\s*([0-9,]{1,7}(?:\.[0-9]{1,2})?)",
        r"Down[:\s]*\$?\s*([0-9,]{1,7}(?:\.[0-9]{1,2})?)",
    ]
    
    for pattern in down_patterns:
        down_m = re.search(pattern, text, re.IGNORECASE)
        if down_m:
            amount = down_m.group(1).replace(",", "")
            data_core["down_payment"] = f"${amount}"
            break
    makes = ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Audi", "Kia", "Hyundai", "Porsche", "Volkswagen", "Nissan", "Chevrolet"]
    for mk in makes:
        m = re.search(r"\b" + re.escape(mk) + r"\b\s*([A-Za-z0-9\- ]{0,30})", text, re.IGNORECASE)
        if m:
            data_core["make"] = mk
            model_guess = str(m.group(1)).strip()
            if model_guess:
                data_core["model"] = model_guess.split(",")[0].split(" with ")[0].strip()
            break

    # Buyer/seller - IMPROVED to avoid generic "Name" matches
    buyer_patterns = [
        r"(?:Lessee|Buyer|Purchaser|Borrower)\s*Name[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"(?:Lessee|Buyer|Purchaser|Borrower)[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"Name[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*\n.*(?:Date of Birth|DOB|Occupation)",
    ]
    
    seller_patterns = [
        r"(?:Lessor|Seller|Dealer|Lender)\s*Name[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",
        r"(?:Lessor|Seller|Dealer|Lender)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",
        r"Dealer[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",
    ]
    
    for pattern in buyer_patterns:
        buyer_m = re.search(pattern, text)
        if buyer_m:
            name = str(buyer_m.group(1)).strip()
            # Validate it's not just "Name" and has at least first+last
            if name.lower() != "name" and len(name.split()) >= 2:
                # Ensure no numbers or special chars
                if not re.search(r'[0-9$@#]', name):
                    data_core["buyer_name"] = name
                    break
    
    for pattern in seller_patterns:
        seller_m = re.search(pattern, text)
        if seller_m:
            name = str(seller_m.group(1)).strip()
            if name.lower() != "name" and len(name.split()) >= 2:
                if not re.search(r'[0-9$@#]', name):
                    data_core["seller_name"] = name
                    break

    # Signature detection - FIXED
    if re.search(r"signature[s]?\s*[:\-]?", text, re.IGNORECASE):
        if re.search(r"buyer signature|signed by buyer", text, re.IGNORECASE):
            sig["buyer_signed"] = True
        if re.search(r"seller signature|signed by seller|dealer signature", text, re.IGNORECASE):
            sig["seller_signed"] = True
        sig_blocks = re.findall(r"([A-Z][A-Za-z ,.'\-]{2,80}\s*\n?\s*signature)", text, re.IGNORECASE)
        # CRITICAL FIX: Convert all matches to strings
        sig["signature_blocks"] = [str(s) for s in sig_blocks[:5]]

    # Fees - FIXED
    fees_found = re.findall(r"([A-Z,a-z\s]{0,30}fee[s]?[^\$]{0,20}\$[0-9,]{1,7}(?:\.[0-9]{1,2})?)", text, re.IGNORECASE)
    cleaned_fees = []
    for f in fees_found:
        cleaned = re.sub(r"\s+", " ", str(f)).strip()
        cleaned_fees.append(cleaned)
    data_core["other_fees"] = cleaned_fees

    # Risk scoring
    risk_score = 100
    high = []
    med = []
    low = []

    try:
        if data_core.get("apr"):
            apr_val = float(str(data_core["apr"]).replace("%", ""))
            if apr_val >= 12:
                high.append(f"High APR: {apr_val}%")
                risk_score -= 40
            elif apr_val >= 8:
                med.append(f"Elevated APR: {apr_val}%")
                risk_score -= 20
            else:
                low.append(f"APR: {apr_val}%")
    except Exception:
        pass

    if re.search(r"early termination|termination fee|foreclosure fee", text, re.IGNORECASE):
        med.append("Early termination penalties mentioned")
        risk_score -= 15

    if re.search(r"late fee|40 per missed|late payment", text, re.IGNORECASE):
        med.append("Late payment penalties present")
        risk_score -= 10

    risk_score = max(0, min(100, int(risk_score)))
    risk["risk_score"] = str(risk_score)
    risk["high_risks"] = high
    risk["medium_risks"] = med
    risk["low_risks"] = low

    # Build final result
    result = {
        "core": data_core,
        "financial_analysis": fin,
        "signature_audit": sig,
        "risk_analysis": risk,
        "raw_debug": {
            "regex_hits": {
                "vin": data_core.get("vin"),
                "vehicle_price": fin.get("vehicle_price"),
                "apr": data_core.get("apr"),
                "monthly_payment": data_core.get("monthly_payment"),
                "term_months": data_core.get("term_months"),
            },
            "sample_text_snippet": txt[:1000]
        }
    }

    return result