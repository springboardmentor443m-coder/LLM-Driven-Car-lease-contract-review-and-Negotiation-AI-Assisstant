"""
Phase 4: SLA Extraction Service (Hybrid: Regex + LLM)
SAFE VERSION – never crashes on 'Unknown'
"""

from typing import Dict
import re
from ..ocr_utils import extract_sla_info


# ======================================================
# DEFAULT SLA (DB-SAFE)
# ======================================================
def get_default_sla() -> Dict:
    return {
        "apr": 0.0,
        "lease_term": 0,
        "monthly_payment": 0.0,
        "mileage_limit": 0,
        "early_termination": "Unknown",
        "penalties": "Unknown",
        "fairness_score": 5,
    }


# ======================================================
# SAFE CAST HELPERS (🔥 CRITICAL)
# ======================================================
def safe_float(value, default=0.0):
    try:
        if value in [None, "", "Unknown"]:
            return default
        return float(str(value).replace("%", "").replace(",", "").strip())
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        if value in [None, "", "Unknown"]:
            return default
        return int(float(str(value).replace(",", "").strip()))
    except Exception:
        return default


# ======================================================
# REGEX EXTRACTION (HIGH CONFIDENCE)
# ======================================================
def extract_basic_fields(text: str) -> Dict:
    data = {}

    # APR / Interest Rate
    apr = re.search(r"(Interest Rate|APR)\s*[:\-]?\s*([\d.]+)%", text, re.IGNORECASE)
    if apr:
        data["apr"] = safe_float(apr.group(2))

    # Monthly EMI / Payment
    emi = re.search(
        r"(Monthly EMI|Monthly Payment)\s*(of)?\s*\$([\d,]+)",
        text,
        re.IGNORECASE,
    )
    if emi:
        data["monthly_payment"] = safe_float(emi.group(3))

    # Lease / Loan Term
    term = re.search(r"(\d+)\s*(months|month)", text, re.IGNORECASE)
    if term:
        data["lease_term"] = safe_int(term.group(1))

    # Mileage limit
    mileage = re.search(r"([\d,]+)\s*(miles|mi)/year", text, re.IGNORECASE)
    if mileage:
        data["mileage_limit"] = safe_int(mileage.group(1))

    return data


# ======================================================
# PHASE 4 MAIN FUNCTION (🔥 NEVER FAILS)
# ======================================================
def extract_sla_from_text(contract_text: str) -> Dict:
    if not contract_text or len(contract_text.strip()) < 50:
        return get_default_sla()

    # Step 1: Regex extraction (trusted)
    regex_data = extract_basic_fields(contract_text)

    # Step 2: LLM extraction (best-effort)
    try:
        llm_data = extract_sla_info(contract_text)
        if not isinstance(llm_data, dict):
            llm_data = {}
    except Exception as e:
        print("⚠️ LLM extraction failed:", e)
        llm_data = {}

    default = get_default_sla()

    # Step 3: Merge (regex > llm > default)
    return {
        "apr": regex_data.get(
            "apr", safe_float(llm_data.get("apr"), default["apr"])
        ),
        "lease_term": regex_data.get(
            "lease_term", safe_int(llm_data.get("lease_term"), default["lease_term"])
        ),
        "monthly_payment": regex_data.get(
            "monthly_payment",
            safe_float(llm_data.get("monthly_payment"), default["monthly_payment"]),
        ),
        "mileage_limit": regex_data.get(
            "mileage_limit",
            safe_int(llm_data.get("mileage_limit"), default["mileage_limit"]),
        ),
        "early_termination": llm_data.get(
            "early_termination", default["early_termination"]
        ),
        "penalties": llm_data.get(
            "penalties", default["penalties"]
        ),
        "fairness_score": safe_int(
            llm_data.get("fairness_score"), default["fairness_score"]
        ),
    }
